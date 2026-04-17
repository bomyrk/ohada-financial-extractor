"""
Metadata extraction module for OHADA financial statements.

This module extracts company-level metadata from Fiche R2 (ficher2_a),
using the preprocessed note values produced by the extraction engine.
"""

from __future__ import annotations
from typing import Optional, Dict, Any
import numpy as np

from .statement import CompanyMetadata
from .schemas import (
    fetch_currency,
    fetch_legal_form,
    fetch_headquarter_country,
    fetch_regime_fiscal,
    LEGAL_FORMS,
    SIEGE_SOCIAL,
    CODES_FISCAUX
)


class CompanyMetadataExtractor:
    """
    Extract structured company metadata from OHADA notes,
    specifically from Fiche R2 (ficher2_a).
    """

    @staticmethod
    def from_fiche_r2(f2a: np.ndarray) -> CompanyMetadata:
        """
        Extract company metadata from the preprocessed Fiche R2 array.

        Expected layout (based on your original implementation):
            Row 0 → Legal form code
            Row 1 → Country code (also used for currency)
            Row 3 → Fiscal regime code
            Row 5 → Year of creation

        Args:
            f2a (np.ndarray): Preprocessed Fiche R2 block (ficher2_a).

        Returns:
            CompanyMetadata: Structured metadata object.
        """

        # Extract raw codes from the last column (latest year)
        legal_form_code = f2a[0, -1]
        country_code = f2a[1, -1]
        regime_fiscal_code = f2a[3, -1]
        year_creation = f2a[5, -1]

        return CompanyMetadata(
            currency=fetch_currency(country_code),
            legal_form=fetch_legal_form(legal_form_code, LEGAL_FORMS),
            country=fetch_headquarter_country(country_code, SIEGE_SOCIAL),
            year_creation=int(year_creation) if str(year_creation).isdigit() else None,
            regime_fiscal=fetch_regime_fiscal(regime_fiscal_code, CODES_FISCAUX)
        )

    # ---------------------------------------------------------
    # NOTE 31 (other_data) — Dividend, Shares, Employees
    # ---------------------------------------------------------
    @staticmethod
    def extract_kpis_from_other(other_data: Optional[np.ndarray]) -> Dict[str, Optional[np.ndarray]]:
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
        number_of_shares = np.sum(values[1:4:, :], axis=0, where=(values[1:4:, :] != None), initial=0) if values.shape[0] > 4 else None
        number_of_employees = np.sum(values[-2:, :], axis=0, where=(values[-2:, :] != None), initial=0) if values.shape[0] >= 2 else None

        return {
            "dividend": dividend,
            "number_of_shares": number_of_shares,
            "number_of_employees": number_of_employees,
        }

    @staticmethod
    def extract_from_statement(statement) -> Optional[CompanyMetadata]:
        """
        High-level helper: extract metadata directly from a FinancialStatement.
        Combines:
            - Fiche R2 metadata
            - NOTE 31 KPIs

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
        kpis = CompanyMetadataExtractor.extract_kpis_from_other(statement.other_data)

        metadata.dividend = kpis["dividend"]
        metadata.number_of_shares = kpis["number_of_shares"]
        metadata.number_of_employees = kpis["number_of_employees"]

        return metadata
