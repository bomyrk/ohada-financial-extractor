"""
Financial Statement Data Container

Represents extracted and structured financial data from OHADA Excel files.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
# from decimal import Decimal
import numpy as np
import pandas as pd
import xarray as xr

from .schemas import (
    ASSETS_ACCOUNTS,
    LIABILITIES_ACCOUNTS,
    INCOME_ACCOUNTS,
    CASHFLOW_ACCOUNTS,
    OTHER_ACCOUNTS,
)

# ----------------------------------------------------------------------
#  COMPANY METADATA MODEL
# ----------------------------------------------------------------------


@dataclass
class CompanyMetadata:
    """
    Structured company metadata extracted from Fiche R2.
    """

    currency: Optional[str] = None
    legal_form: Optional[str] = None
    country: Optional[str] = None
    year_creation: Optional[int] = None
    regime_fiscal: Optional[str] = None
    dividend: Optional[np.ndarray] = None
    number_of_shares: Optional[np.ndarray] = None
    number_of_employees: Optional[np.ndarray] = None

    def to_dict(self):
        """Convert metadata to JSON‑friendly dict."""

        def convert(v):
            if isinstance(v, np.ndarray):
                if v.size == 1:
                    return v.item()
                return v.tolist()
            return v

        return {k: convert(v) for k, v in self.__dict__.items()}

    def missing_fields(self):
        """Return a list of metadata fields that are None or empty."""
        missing = []
        for field_name, value in self.__dict__.items():
            if value is None:
                missing.append(field_name)
            elif isinstance(value, np.ndarray) and value.size == 0:
                missing.append(field_name)
        return missing


# ----------------------------------------------------------------------
#  FINANCIAL STATEMENT MODEL
# ----------------------------------------------------------------------
@dataclass
class FinancialStatement:
    """
    Container for extracted financial statement data.

    Attributes:
        _asset_data: NumPy array of balance sheet assets
        _liability_data: NumPy array of balance sheet liabilities
        _income_data: NumPy array of income statement data
        _cashflow_data: NumPy array of cash flow statement data
        other_data: Numpy array of note 31 data
        notes (annexes): Dictionary of notes data
        periods: List of period dates (e.g., ['2023-12-31', '2024-12-31'])
        file_path: Original Excel file path
    """

    # Raw Extraction Inputs (Keep private/protected to discourage direct usage)
    _asset_data: Optional[np.ndarray] = None
    _liability_data: Optional[np.ndarray] = None
    _income_data: Optional[np.ndarray] = None
    _cashflow_data: Optional[np.ndarray] = None
    _other_data: Optional[np.ndarray] = None
    # Notes (annexes)
    notes: Optional[Dict[str, Dict[str, Any]]] = None

    # Periods extracted from Fiche R1
    periods: Optional[List[str]] = None

    # Path to the file(s) used for extraction
    file_path: Optional[str] = None

    # Company metadata extracted from Fiche R2
    metadata: Optional[CompanyMetadata] = None

    # Cached xarray Datasets
    _arrays_cache: Optional[Dict[str, xr.DataArray]] = field(
        default=None, init=False, repr=False
    )

    @property
    def arrays(self) -> Dict[str, xr.DataArray]:
        """Lazily builds and returns the unified xarray Dataset."""
        if self._arrays_cache is None:
            self._arrays_cache = self._build_arrays()
        return self._arrays_cache

    # Clean, unified entry points for the user
    @property
    def asset(self) -> xr.DataArray:
        return self.arrays["asset"]

    @property
    def liability(self) -> xr.DataArray:
        return self.arrays["liability"]

    @property
    def income(self) -> xr.DataArray:
        return self.arrays["income"]

    @property
    def cashflow(self) -> xr.DataArray:
        return self.arrays["cashflow"]

    @property
    def other(self) -> xr.DataArray:
        return self.arrays["other"]

    @property
    def years(self) -> pd.DatetimeIndex:
        """
        Get the list of periods/years dynamically from the xarray structures.
        Returns a clean pandas DatetimeIndex.
        """
        # On extrait l'index de la dimension 'annee' de n'importe quel tableau (ex: asset)
        if self.asset is not None:
            return pd.DatetimeIndex(self.asset.coords["annee"].values)

        # Fallback au cas où l'objet est vide
        return pd.DatetimeIndex([])

    def __post_init__(self):
        if self.periods is None:
            self.periods = []

    # ------------------------------------------------------------------
    #  NEW: Convert numpy → xarray for validation + visualization
    # ------------------------------------------------------------------
    def _build_arrays(self) -> Dict[str, xr.DataArray]:
        """
        Convert numpy arrays into xarray DataArrays with MultiIndex accounts.
        This enables validation and visualization layers.
        """

        if not self.periods:
            raise ValueError(
                "Periods must be populated to build the analytical dataset."
            )

        n_years = len(self.periods)
        # Convert periods to datetime index
        years_idx = (
            pd.Index(pd.to_datetime(self.periods), name="annee")
            if n_years > 2
            else pd.Index(pd.to_datetime(self.periods[::-1]), name="annee")
        )

        def create_index(data):
            return pd.MultiIndex.from_tuples(data, names=["Label", "Reference"])

        # Build MultiIndex accounts
        asset_accounts = create_index(ASSETS_ACCOUNTS)
        liabilities_accounts = create_index(LIABILITIES_ACCOUNTS)
        income_accounts = create_index(INCOME_ACCOUNTS)
        cashflow_accounts = create_index(CASHFLOW_ACCOUNTS)
        other_accounts = create_index(OTHER_ACCOUNTS)

        # --------------------------------------------------------------
        # Helper: reshape numpy → (account, year, value_type)
        # --------------------------------------------------------------
        def reshape_statement(data, value_types):
            if data is None:
                return None

            # Remove reference column
            values = data[:, 1:]

            # Conversion de la matrice NumPy en objets Decimal
            # (Idéalement, convertissez depuis des chaînes de caractères ou des int pour éviter les résidus de floats)
            # make_decimal = np.vectorize(lambda x: Decimal(str(x)) if x is not None else Decimal('0.00'))
            # values = make_decimal(values)

            n_types = len(value_types)

            if n_years == 2:
                # Replace None with 0
                values = np.where(values == None, 0, values)
                if n_types == 3:
                    values = np.hstack(
                        (
                            np.insert(
                                values.copy()[:, [-1]], [0], [np.nan, np.nan], axis=1
                            ),
                            values.copy()[:, 0:-1],
                        )
                    )
                else:
                    values = np.hstack((values.copy()[:, [-1]], values.copy()[:, 0:-1]))

            # Expected shape = (n_accounts, n_years * n_types)
            expected_cols = n_years * n_types

            if values.shape[1] != expected_cols:
                raise ValueError(
                    f"Invalid shape for statement: expected {expected_cols} columns, got {values.shape[1]}"
                )

            reshaped = (
                values.reshape(values.shape[0], n_years, n_types)
                if n_types > 1
                else values
            )
            return reshaped

        # --------------------------------------------------------------
        # Build xarray DataArrays
        # --------------------------------------------------------------
        asset_da = (
            xr.DataArray(
                data=reshape_statement(
                    self._asset_data, ["Gross", "Amortissement", "Net"]
                ),
                coords={
                    "compte": asset_accounts,
                    "annee": years_idx,
                    "valeur": ["Gross", "Amortissement", "Net"],
                },
                dims=("compte", "annee", "valeur"),
                name="asset",
            )
            .astype(float)
            .round(2)
        )

        liability_da = (
            xr.DataArray(
                data=reshape_statement(self._liability_data, ["Net"]),
                coords={"compte": liabilities_accounts, "annee": years_idx},
                dims=("compte", "annee"),
                name="liability",
            )
            .astype(float)
            .round(2)
        )

        income_da = (
            xr.DataArray(
                data=reshape_statement(self._income_data, ["Net"]),
                coords={"compte": income_accounts, "annee": years_idx},
                dims=("compte", "annee"),
                name="income",
            )
            .astype(float)
            .round(2)
        )

        cashflow_da = (
            xr.DataArray(
                data=reshape_statement(self._cashflow_data, ["Net"]),
                coords={"compte": cashflow_accounts, "annee": years_idx},
                dims=("compte", "annee"),
                name="cashflow",
            )
            .astype(float)
            .round(2)
        )

        other_data_da = xr.DataArray(
            data=reshape_statement(self._other_data, ["Net"]),
            coords={"compte": other_accounts, "annee": years_idx},
            dims=("compte", "annee"),
            name="other",
        ).astype(int)

        return {
            "asset": asset_da,
            "liability": liability_da,
            "income": income_da,
            "cashflow": cashflow_da,
            "other": other_data_da,
        }

    # ---------------------------------------------------------
    # INTERNAL HELPERS
    # ---------------------------------------------------------
    def _convert_array(self, arr):
        if arr is None:
            return None
        return arr.tolist()

    def _convert_notes(self, notes_dict):
        if notes_dict is None:
            return None

        out = {}
        for key, entry in notes_dict.items():
            out[key] = {
                "name": entry.get("name"),
                "raw_value": self._convert_array(entry.get("raw_value")),
                "preprocess_value": self._convert_array(entry.get("preprocess_value")),
            }
        return out

    # ---------------------------------------------------------
    # EXPORT METHODS
    # ---------------------------------------------------------

    @property
    def to_numpy(self) -> Dict[str, np.ndarray]:
        """
        Renvoie un dictionnaire contenant les matrices NumPy nettoyées,
        remodelées et prêtes à l'emploi (SANS colonne de référence).
        Idéal pour le calcul matriciel et les modèles mathématiques.
        Structure de l'actif : (n_comptes, n_annees, 3).
        """
        return {key: da.values for key, da in self.arrays.items()}

    @property
    def to_raw_numpy(self) -> Dict[str, Optional[np.ndarray]]:
        """
        Renvoie les matrices NumPy d'extraction originales AVEC la colonne de référence.
        Idéal pour les exports Excel, la traçabilité OHADA et les RECHERCHEV.
        """
        return {
            "asset": self._asset_data,
            "liability": self._liability_data,
            "income": self._income_data,
            "cashflow": self._cashflow_data,
            "other": self._other_data,
        }

    def to_dict(
        self, include_metadata: bool = True, include_notes: bool = True
    ) -> Dict[str, Any]:
        """
        Convertit l'état financier en un dictionnaire JSON-serializable.
        Contient les données brutes AVEC les colonnes de référence.

        Args:
            include_metadata: Si True, inclut les métadonnées de l'entreprise.
            include_notes: Si True, inclut les dictionnaires d'annexes (notes).
        """
        data = {
            "assets": self._convert_array(self._asset_data),
            "liabilities": self._convert_array(self._liability_data),
            "income": self._convert_array(self._income_data),
            "cashflow": self._convert_array(self._cashflow_data),
            "other": self._convert_array(self._other_data),
            "periods": self.periods,
            "file_path": self.file_path,
        }

        if include_metadata:
            data["metadata"] = self.metadata.to_dict() if self.metadata else None

        if include_notes:
            data["notes"] = self._convert_notes(self.notes)

        return data

    def to_json(self) -> Dict[str, Any]:
        """Alias for JSON‑safe export."""
        return self.to_dict()

    # ---------------------------------------------------------
    # GETTERS FOR SPECIFIC ACCOUNTS
    # ---------------------------------------------------------
    def get_asset(self, reference: str) -> xr.DataArray:
        """Query your asset data natively via reference code (e.g. 'CA')."""
        # This searches your MultiIndex 'compte' seamlessly
        return self.asset.sel(Reference=reference)

    def get_liability(self, reference: str) -> xr.DataArray:
        """Query your liability data natively via reference code."""
        # This searches your MultiIndex 'compte' seamlessly
        return self.liability.sel(Reference=reference)

    def get_income(self, reference: str) -> xr.DataArray:
        """Query your income data natively via reference code."""
        # This searches your MultiIndex 'compte' seamlessly
        return self.income.sel(Reference=reference)

    def get_cashflow(self, reference: str) -> xr.DataArray:
        """Query your cashflow data natively via reference code."""
        # This searches your MultiIndex 'compte' seamlessly
        return self.cashflow.sel(Reference=reference)

    def get_other(self, reference: str) -> Optional[np.ndarray]:
        """Query your other data natively via reference code."""
        return self.other.sel(compte=reference)

    # ---------------------------------------------------------
    # GETTERS FOR NOTES
    # ---------------------------------------------------------
    def get_note(self, key: str, processed: bool = False):
        """
        Retrieve a note by its key.

        Args:
            key: The note identifier (e.g., 'note3a', 'note5', 'ficher2_a')
            processed: If True, return the preprocessed value instead of raw.

        Returns:
            The requested note array, or None if not found.
        """
        if self.notes is None:
            return None

        entry = self.notes.get(key)
        if entry is None:
            return None

        return entry.get("preprocess_value") if processed else entry.get("raw_value")

    def get_note_by_name(self, name: str, processed: bool = False):
        """
        Retrieve a note by its human-readable name.

        Args:
            name: The human-readable name of the note (e.g., 'IMMOBILISATION BRUTE')
            processed: If True, return the preprocessed value instead of raw.

        Returns:
            The requested note array, or None if not found.
        """
        if self.notes is None:
            return None

        name = name.strip().lower()

        for key, entry in self.notes.items():
            if entry.get("name", "").strip().lower() == name:
                return (
                    entry.get("preprocess_value")
                    if processed
                    else entry.get("raw_value")
                )

        return None

    def plot(self, *args, **kwargs):
        from ohada_extractor.visualization.base_plotter import plot_router

        plot_router(self, *args, **kwargs)
