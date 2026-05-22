"""
Metadata extraction module for OHADA financial statements.

This module extracts company-level metadata from Fiche R2 (ficher2_a),
using the preprocessed note values produced by the extraction engine.
"""

from __future__ import annotations

import unicodedata
from typing import Any, Dict, List, Optional

import numpy as np

from .schemas import (
    CODES_FISCAUX,
    LEGAL_FORMS,
    NORMALIZED_ACTIVITY_MAP,
    SIEGE_SOCIAL,
    fetch_currency,
    fetch_headquarter_country,
    fetch_legal_form,
    fetch_regime_fiscal,
)
from .statement import CompanyMetadata


def normalize_label(label: str) -> str:
    if not label or str(label).strip() == "":
        return ""

    # lowercase + remove accents
    key = unicodedata.normalize("NFKD", label).encode("ascii", "ignore").decode().lower().strip()

    # direct match
    if key in NORMALIZED_ACTIVITY_MAP:
        return NORMALIZED_ACTIVITY_MAP[key]

    # fallback: return cleaned label
    return label.strip()


def is_true(x):
    return str(x).strip() not in ("0", "", ".", "-", "None", "none", "N/A", "n/a", "NA", "na", "0.0")


def safe_float(x) -> float:
    try:
        return float(str(x).replace(",", "."))
    except Exception:
        return 0.0


class CompanyMetadataExtractor:
    """
    Extract structured company metadata from OHADA notes,
    specifically from Fiche R2 (ficher2_a, preprocessed),
    note 31 (other_data, raw).
    """

    @staticmethod
    def classify_trend(growth: Optional[float]) -> Optional[str]:
        if growth is None:
            return None
        if growth > 5:
            return "expanding"
        if growth < -5:
            return "declining"
        return "stable"

    @staticmethod
    def from_fiche_r2(f2a: np.ndarray) -> CompanyMetadata:
        """
        Extract company metadata from the preprocessed Fiche R2 array.

        Expected layout (based on your original implementation):
            Row 0 → Legal form code
            Row 1 → Country code (also used for currency)
            Row 2 → Number of units
            Row 3 → Fiscal regime code
            Row 5 → Year of creation
            Row 7 → Private ownership
            Row 6 → Public ownership
            Row 8 → Foreign ownership


        Args:
            f2a (np.ndarray): Preprocessed Fiche R2 block (ficher2_a).

        Returns:
            CompanyMetadata: Structured metadata object.
        """

        # Extract raw codes from the last column (latest year)
        legal_form_code = f2a[0, -1]
        country_code = f2a[1, -1]
        nbr_unites = f2a[2, -1]
        regime_fiscal_code = f2a[3, -1]
        year_creation = f2a[5, -1]
        pub_owned = is_true(f2a[6, -1])
        pri_owned = is_true(f2a[7, -1])
        fgn_owned = is_true(f2a[8, -1])
        if pub_owned:
            owned = "Public"
        elif pri_owned:
            owned = "Private"
        elif fgn_owned:
            owned = "Foreign"
        else:
            owned = "None"

        return CompanyMetadata(
            currency=fetch_currency(country_code),
            legal_form=fetch_legal_form(legal_form_code, LEGAL_FORMS),
            country=fetch_headquarter_country(country_code, SIEGE_SOCIAL),
            year_creation=int(year_creation) if str(year_creation).isdigit() else None,
            regime_fiscal=fetch_regime_fiscal(regime_fiscal_code, CODES_FISCAUX),
            number_of_units=int(nbr_unites) if str(nbr_unites).isdigit() else None,
            owned=owned,
        )

    @staticmethod
    def from_fiche_r2_ext(f2a_ext: np.ndarray) -> Dict[str, Any]:
        """
        Extract OHADA activity breakdown with:
        - normalized labels
        - safe numeric parsing
        - percentages
        - primary vs secondary activities

        Structure:
            Every 4 columns = one year:
                [label, reference, value, percentage]

        """

        def safe_int(x):
            try:
                return int(float(str(x).replace(",", ".")))
            except (ValueError, TypeError):
                return 0

        n_cols = f2a_ext.shape[1]
        if n_cols % 4 != 0:
            raise ValueError("Invalid ficher2_a_ext structure: columns must be multiple of 4")

        n_years = n_cols // 4
        activities_by_year = {}

        for year_idx in range(n_years):
            start = year_idx * 4
            end = start + 4

            year_block = f2a_ext[:, start:end]

            activities = []
            for row in year_block:
                label = normalize_label(row[0].strip())
                reference = str(row[1]).strip()
                value = safe_float(row[2])
                pct = safe_float(row[3])

                activities.append(
                    {
                        "label_raw": str(row[0].strip()),
                        "label": label if label else "Activity",
                        "reference": reference,
                        "value": value,
                        "percentage": pct,
                    }
                )

            # Sort by value
            activities.sort(key=lambda x: x["value"], reverse=True)

            # -------------------------------
            # 1. Check if provided % are valid
            # -------------------------------
            pct_sum = sum(a["percentage"] for a in activities)

            pct_valid = pct_sum > 0 and 99 <= pct_sum <= 101  # tolerance for rounding

            # -------------------------------
            # 2. If invalid → recompute from values
            # -------------------------------
            if not pct_valid:
                total_value = sum(a["value"] for a in activities) or 1
                for a in activities:
                    a["percentage"] = round((a["value"] / total_value) * 100, 2)

            # -------------------------------
            # 3. Fix rounding drift to ensure sum = 100
            # -------------------------------
            drift = 100 - sum(a["percentage"] for a in activities)
            activities[0]["percentage"] += drift

            activities_by_year[year_idx] = {
                "activities_breakdown": activities,
                "main_activity": activities[0] if activities else None,
                "secondary_activities": activities[1:] if len(activities) > 1 else [],
            }

        # Latest year = last block
        latest = activities_by_year[n_years - 1]

        if len(activities_by_year) == 1:
            yoy_growth = {}
        else:
            yoy_growth = CompanyMetadataExtractor.compute_yoy_growth(activities_by_year)

        return {
            "activities_breakdown": latest["activities_breakdown"],
            "main_activity": latest["main_activity"],
            "secondary_activities": latest["secondary_activities"],
            "activities_by_year": activities_by_year,
            "yoy_growth": yoy_growth,
            "ranking_changes": CompanyMetadataExtractor.compute_ranking_changes(activities_by_year),
            "sector_concentration": CompanyMetadataExtractor.compute_sector_concentration(activities_by_year),
        }

    @staticmethod
    def compute_yoy_growth(activities_by_year: Dict[int, Dict]) -> Dict[int, List[Dict]]:
        """
        Compute YoY growth for each activity based on its reference code.
        Returns:
            {
                1: [ {reference, label, value_prev, value_curr, yoy_growth}, ... ],
                2: [...],
                ...
            }
        """
        yoy = {}

        years = sorted(activities_by_year.keys())

        for idx in range(1, len(years)):
            prev_year = years[idx - 1]
            curr_year = years[idx]

            prev_acts = {a["reference"]: a for a in activities_by_year[prev_year]["activities_breakdown"]}
            curr_acts = {a["reference"]: a for a in activities_by_year[curr_year]["activities_breakdown"]}

            yoy[curr_year] = []

            for ref, curr in curr_acts.items():
                prev = prev_acts.get(ref)

                if prev is None:
                    growth = None
                else:
                    v_prev = prev["value"]
                    v_curr = curr["value"]

                    if v_prev > 0:
                        growth = round(((v_curr - v_prev) / v_prev) * 100, 2)
                    else:
                        growth = None

                yoy[curr_year].append(
                    {
                        "reference": ref,
                        "label": curr["label"],
                        "value_prev": prev["value"] if prev else None,
                        "value_curr": curr["value"],
                        "yoy_growth": growth,
                        "trend": CompanyMetadataExtractor.classify_trend(growth),
                    }
                )

        return yoy

    @staticmethod
    def compute_ranking_changes(activities_by_year: Dict[int, Dict]) -> Dict[int, List[Dict]]:
        ranking_changes = {}
        years = sorted(activities_by_year.keys())

        for idx in range(1, len(years)):
            prev_year = years[idx - 1]
            curr_year = years[idx]

            prev_list = activities_by_year[prev_year]["activities_breakdown"]
            curr_list = activities_by_year[curr_year]["activities_breakdown"]

            prev_rank = {a["reference"]: rank for rank, a in enumerate(prev_list)}
            curr_rank = {a["reference"]: rank for rank, a in enumerate(curr_list)}

            ranking_changes[curr_year] = []

            for ref, rank_now in curr_rank.items():
                if ref not in prev_rank:
                    movement = None  # new activity
                else:
                    movement = prev_rank[ref] - rank_now  # positive = moved up

                ranking_changes[curr_year].append(
                    {
                        "reference": ref,
                        "label": curr_list[rank_now]["label"],
                        "previous_rank": prev_rank.get(ref),
                        "current_rank": rank_now,
                        "movement": movement,
                    }
                )

        return ranking_changes

    @staticmethod
    def compute_sector_concentration(activities_by_year: Dict[int, Dict]) -> Dict[int, float]:
        """
        The Herfindahl - Hirschman Index measure concentrtion

        We use percentage (0-100), so HHI ranges:
        - Low concentration -> <1800
        - Moderate concentration -> 1800-2500
        - High concentration -> 2500+

        Returns:
            - {year: hhi}
        """
        hhi = {}

        for year, data in activities_by_year.items():
            percentages = [a["percentage"] for a in data["activities_breakdown"]]
            hhi[year] = round(sum((p**2) for p in percentages), 2)

        return hhi

    # ---------------------------------------------------------
    # Note 31 (other_data) — Dividend, Shares, Employees
    # ---------------------------------------------------------
    @staticmethod
    def extract_kpis_from_other(
        other_data: Optional[np.ndarray],
    ) -> Dict[str, Optional[np.ndarray]]:
        """
        Extract dividend, number of shares, and number of employees from NOTE 31.

        Expected layout (based on your previous implementation):
            - Dividend: row 9
            - Number of shares: rows 1 to 3
            - Number of employees: last 2 rows
        """
        if other_data is None:
            return {
                "dividend": None,
                "number_of_shares": None,
                "number_of_employees": None,
            }

        # Remove reference column
        values = other_data[:, 1:]

        dividend = values[9, :] if values.shape[0] > 9 else None
        if values.shape[0] > 4:
            shares = (
                np.array([safe_float(v) for v in values[1:4, :].flatten()]).reshape(values[1:4, :].shape).sum(axis=0)
            )
        else:
            shares = None

        if values.shape[0] >= 2:
            employees = (
                np.array([safe_float(v) for v in values[-2:, :].flatten()]).reshape(values[-2:, :].shape).sum(axis=0)
            )
        else:
            employees = None

        return {
            "dividend": dividend,
            "number_of_shares": shares,
            "number_of_employees": employees,
        }

    @staticmethod
    def extract_from_statement(statement) -> Optional[CompanyMetadata]:
        """
        High-level helper: extract metadata directly from a FinancialStatement.
        Combines:
            - Fiche R2 metadata
            - Note 31 KPIs

        Args:
            statement (FinancialStatement): The extracted financial statement.

        Returns:
            CompanyMetadata or None
        """
        f2a = statement.get_note("ficher2_a", processed=True)

        if f2a is None:
            return None

        # Base metadata from Fiche R2
        metadata = CompanyMetadataExtractor.from_fiche_r2(f2a)

        # Add KPIs from NOTE 31
        kpis = CompanyMetadataExtractor.extract_kpis_from_other(
            statement.other.values if statement.other is not None else None
        )

        metadata.dividend = kpis["dividend"]
        metadata.number_of_shares = kpis["number_of_shares"]
        metadata.number_of_employees = kpis["number_of_employees"]

        # Add metadata from Fiche R2 extension
        f2b = statement.get_note("ficher2_b", processed=True)
        if f2b is not None:
            metadata_ext = CompanyMetadataExtractor.from_fiche_r2_ext(f2b)
            metadata.activities_breakdown = metadata_ext["activities_breakdown"]
            metadata.main_activity = metadata_ext["main_activity"]
            metadata.secondary_activities = metadata_ext["secondary_activities"]
            metadata.activities_by_year = metadata_ext["activities_by_year"]
            metadata.yoy_growth = metadata_ext["yoy_growth"]
            metadata.ranking_changes = metadata_ext["ranking_changes"]
            metadata.sector_concentration = metadata_ext["sector_concentration"]

        return metadata
