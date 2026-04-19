"""
Financial Statement Data Container

Represents extracted and structured financial data from OHADA Excel files.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import numpy as np
import pandas as pd
import xarray as xr

from .schemas import (
    ASSETS_ACCOUNTS,
    LIABILITIES_ACCOUNTS,
    INCOME_ACCOUNTS,
    CASHFLOW_ACCOUNTS,
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
        asset_data: NumPy array of balance sheet assets
        liability_data: NumPy array of balance sheet liabilities
        income_data: NumPy array of income statement data
        cashflow_data: NumPy array of cash flow statement data
        other_data: Numpy array of note 31 data
        notes (annexes): Dictionary of notes data
        periods: List of period dates (e.g., ['2023-12-31', '2024-12-31'])
        file_path: Original Excel file path
    """
    asset_data: Optional[np.ndarray] = None
    liability_data: Optional[np.ndarray] = None
    income_data: Optional[np.ndarray] = None
    cashflow_data: Optional[np.ndarray] = None
    other_data: Optional[np.ndarray]=None
    # Notes (annexes)
    notes: Optional[Dict[str, Dict[str, Any]]] = None

    # Periods extracted from Fiche R1
    periods: Optional[List[str]] = None

    # Path to the file(s) used for extraction
    file_path: Optional[str] = None

    # NEW: Company metadata extracted from Fiche R2
    metadata: Optional[CompanyMetadata] = None

    # NEW: xarray objects (populated by to_xarray())
    asset: Optional[xr.DataArray] = None
    liability: Optional[xr.DataArray] = None
    income: Optional[xr.DataArray] = None
    cashflow: Optional[xr.DataArray] = None

    # NEW: MultiIndex accounts
    asset_accounts: Optional[pd.MultiIndex] = None
    liabilities_accounts: Optional[pd.MultiIndex] = None
    income_accounts: Optional[pd.MultiIndex] = None
    cashflow_accounts: Optional[pd.MultiIndex] = None

    # NEW: datetime index for periods
    years: Optional[pd.Index] = None

    def __post_init__(self):
        if self.periods is None:
            self.periods = []

    # ------------------------------------------------------------------
    #  NEW: Convert numpy → xarray for validation + visualization
    # ------------------------------------------------------------------
    def to_xarray(self):
        """
        Convert numpy arrays into xarray DataArrays with MultiIndex accounts.
        This enables validation and visualization layers.
        """

        if not self.periods:
            raise ValueError("FinancialStatement.periods is empty — cannot build xarray objects.")

        n_years = len(self.periods)
        # Convert periods to datetime index
        self.years = pd.Index(pd.to_datetime(self.periods), name="annee") if n_years > 2 else pd.Index(pd.to_datetime(self.periods[::-1]), name="annee")

        def create_index(data):
            return pd.MultiIndex.from_tuples(data, names=["Label", "Reference"])

        # Build MultiIndex accounts
        self.asset_accounts = create_index(ASSETS_ACCOUNTS)
        self.liabilities_accounts = create_index(LIABILITIES_ACCOUNTS)
        self.income_accounts = create_index(INCOME_ACCOUNTS)
        self.cashflow_accounts = create_index(CASHFLOW_ACCOUNTS)

        # --------------------------------------------------------------
        # Helper: reshape numpy → (account, year, value_type)
        # --------------------------------------------------------------
        def reshape_statement(data, value_types):
            if data is None:
                return None

            # Remove reference column
            values = data[:, 1:]

            n_types = len(value_types)

            if n_years == 2:
                # Replace None with 0
                values = np.where(values == None, 0, values)
                if n_types == 3:
                    values = np.hstack((np.insert(values.copy()[:, [-1]], [0],
                                                 [np.nan, np.nan], axis=1), values.copy()[:, 0:-1]))
                else:
                    values = np.hstack((values.copy()[:, [-1]], values.copy()[:, 0:-1]))

            # Expected shape = (n_accounts, n_years * n_types)
            expected_cols = n_years * n_types

            if values.shape[1] != expected_cols:
                raise ValueError(
                    f"Invalid shape for statement: expected {expected_cols} columns, got {values.shape[1]}"
                )

            reshaped = values.reshape(values.shape[0], n_years, n_types) if n_types > 1 else values
            return reshaped

        # --------------------------------------------------------------
        # Build xarray DataArrays
        # --------------------------------------------------------------
        self.asset = xr.DataArray(
            data=reshape_statement(self.asset_data, ["Gross", "Amortissement", "Net"]),
            coords={
                "compte": self.asset_accounts,
                "annee": self.years,
                "valeur": ["Gross", "Amortissement", "Net"],
            },
            dims=("compte", "annee", "valeur"),
            name="asset",
        ).astype(float).round(2)

        self.liability = xr.DataArray(
            data=reshape_statement(self.liability_data, ["Net"]),
            coords={"compte": self.liabilities_accounts, "annee": self.years},
            dims=("compte", "annee"),
            name="liabilities",
        ).astype(float).round(2)

        self.income = xr.DataArray(
            data=reshape_statement(self.income_data, ["Net"]),
            coords={"compte": self.income_accounts, "annee": self.years},
            dims=("compte", "annee"),
            name="income",
        ).astype(float).round(2)

        self.cashflow = xr.DataArray(
            data=reshape_statement(self.cashflow_data, ["Net"]),
            coords={"compte": self.cashflow_accounts, "annee": self.years},
            dims=("compte", "annee"),
            name="cashflow",
        ).astype(float).round(2)

        return self  # allow chaining

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
    def to_dict(self) -> Dict[str, Any]:
        """Convert statement to dictionary format."""
        return {
            "assets": self._convert_array(self.asset_data),
            "liabilities": self._convert_array(self.liability_data),
            "income": self._convert_array(self.income_data),
            "cashflow": self._convert_array(self.cashflow_data),
            "other": self._convert_array(self.other_data),
            "notes": self._convert_notes(self.notes),
            "periods": self.periods,
            "file_path": self.file_path,
            "metadata": self.metadata.__dict__ if self.metadata else None,
        }

    def to_json(self) -> Dict[str, Any]:
        """Alias for JSON‑safe export."""
        return self.to_dict()

    # ---------------------------------------------------------
    # GETTERS FOR SPECIFIC ACCOUNTS
    # ---------------------------------------------------------
    def get_asset(self, reference: str) -> Optional[np.ndarray]:
        """Get asset row by account reference code."""
        if self.asset_data is None:
            return None
        for i, row in enumerate(self.asset_data):
            if str(row[0]).strip().upper() == reference.upper():
                return row[1:]
        return None

    def get_liability(self, reference: str) -> Optional[np.ndarray]:
        """Get liability row by account reference code."""
        if self.liability_data is None:
            return None
        for i, row in enumerate(self.liability_data):
            if str(row[0]).strip().upper() == reference.upper():
                return row[1:]
        return None

    def get_income(self, reference: str) -> Optional[np.ndarray]:
        """Get income row by account reference code."""
        if self.income_data is None:
            return None
        for i, row in enumerate(self.income_data):
            if str(row[0]).strip().upper() == reference.upper():
                return row[1:]
        return None

    def get_other(self, reference: str) -> Optional[np.ndarray]:
        """Get other row by account reference code."""
        if self.other_data is None:
            return None
        for i, row in enumerate(self.other_data):
            if str(row[0]).strip().upper() == reference.upper():
                return row[1:]
        return None

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
                return entry.get("preprocess_value") if processed else entry.get("raw_value")

        return None

    #
    #
    #
    def plot(self, *args, **kwargs):
        from ohada_extractor.visualization.base_plotter import plot_router
        plot_router(self, *args, **kwargs)
