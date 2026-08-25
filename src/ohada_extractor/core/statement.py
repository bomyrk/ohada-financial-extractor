"""
Financial Statement Data Container

Represents extracted and structured financial data from OHADA Excel files.
"""

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import xarray as xr

from .schemas import (
    ASSETS_ACCOUNTS,
    CASHFLOW_ACCOUNTS,
    INCOME_ACCOUNTS,
    LIABILITIES_ACCOUNTS,
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
    number_of_units: Optional[int] = None
    owned: Optional[str] = None

    # KPI from Note 31
    dividend: Optional[np.ndarray] = None
    number_of_shares: Optional[np.ndarray] = None
    number_of_employees: Optional[np.ndarray] = None

    # Activity-related fields
    activities_breakdown: Optional[List[Dict]] = None
    main_activity: Optional[Dict] = None
    secondary_activities: Optional[List[Dict]] = None

    # Multi-year activity data
    activities_by_year: Optional[Dict[int, Dict]] = None
    yoy_growth: Optional[Dict[int, List[Dict]]] = None
    sector_concentration: Optional[Dict[int, float]] = None
    ranking_changes: Optional[Dict[int, List[Dict]]] = None

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

    def __str__(self) -> str:
        parts = [
            f"legal_form={self.legal_form or 'n/a'}",
            f"country={self.country or 'n/a'}",
            f"currency={self.currency or 'n/a'}",
            f"fiscal_regime={self.regime_fiscal or 'n/a'}",
            f"year_creation={self.year_creation or 'n/a'}",
        ]

        if self.main_activity:
            parts.append(f"main_activity={self.main_activity.get('label', 'n/a')}")

        return f"CompanyMetadata({', '.join(parts)})"


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
        _other_data: Numpy array of note 31 data
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
    _arrays_cache: Optional[Dict[str, xr.DataArray]] = field(default=None, init=False, repr=False)
    SERIALIZATION_SCHEMA_VERSION = "1.0"

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

    def __str__(self) -> str:
        file_label = self.file_path or "n/a"
        periods_label = ", ".join(str(period) for period in self.periods) if self.periods else "n/a"
        notes_count = len(self.notes) if self.notes else 0
        metadata_label = "yes" if self.metadata is not None else "no"

        return (
            "FinancialStatement("
            f"file_path={file_label}, "
            f"periods=[{periods_label}], "
            f"notes={notes_count}, "
            f"metadata={metadata_label}"
            ")"
        )

    def validate_coherence(self, raise_on_error: bool = False) -> bool:
        """
        Validate internal OHADA financial-statement coherence.

        Args:
            raise_on_error: If True, raises ValueError when validation fails.
                If False, returns False and logs validation details.
        """
        from ohada_extractor.validation.coherence_validator import CoherenceValidator

        is_valid = CoherenceValidator.from_financial_statement(self).validate()
        if raise_on_error and not is_valid:
            raise ValueError("Financial statement coherence validation failed.")
        return is_valid

    def build_coherence_report(self):
        """
        Build a detailed OHADA coherence report for this statement.
        """
        from ohada_extractor.validation.coherence_validator import CoherenceValidator

        return CoherenceValidator.from_financial_statement(self).build_report()

    def coherence_report(self):
        """
        Alias for build_coherence_report().
        """
        return self.build_coherence_report()

    def build_metadata(self):
        """
        Extract and attach company metadata for this statement.

        Returns:
            CompanyMetadata or None if the required metadata notes are missing.
        """
        from ohada_extractor.core.metadata_extractor import CompanyMetadataExtractor

        self.metadata = CompanyMetadataExtractor.extract_from_statement(self)
        return self.metadata

    # ------------------------------------------------------------------
    #  NEW: Convert numpy → xarray for validation + visualization
    # ------------------------------------------------------------------
    def _build_arrays(self) -> Dict[str, xr.DataArray]:
        """
        Convert numpy arrays into xarray DataArrays with MultiIndex accounts.
        This enables validation and visualization layers.
        """

        if not self.periods:
            raise ValueError("Periods must be populated to build the analytical dataset.")

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
                            np.insert(values.copy()[:, [-1]], [0], [np.nan, np.nan], axis=1),
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

            reshaped = values.reshape(values.shape[0], n_years, n_types) if n_types > 1 else values
            return reshaped

        # --------------------------------------------------------------
        # Build xarray DataArrays
        # --------------------------------------------------------------
        asset_da = (
            xr.DataArray(
                data=reshape_statement(self._asset_data, ["Gross", "Amortissement", "Net"]),
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

    @staticmethod
    def _to_serializable_value(value):
        if isinstance(value, np.ndarray):
            return {
                "__ndarray__": True,
                "dtype": str(value.dtype),
                "data": FinancialStatement._to_serializable_value(value.tolist()),
            }

        if isinstance(value, np.generic):
            return value.item()

        if isinstance(value, dict):
            return {
                str(FinancialStatement._to_serializable_value(key)): FinancialStatement._to_serializable_value(val)
                for key, val in value.items()
            }

        if isinstance(value, tuple):
            return {
                "__tuple__": True,
                "data": [FinancialStatement._to_serializable_value(item) for item in value],
            }

        if isinstance(value, list):
            return [FinancialStatement._to_serializable_value(item) for item in value]

        return value

    @staticmethod
    def _from_serializable_value(value):
        if isinstance(value, dict):
            if value.get("__ndarray__") is True:
                data = FinancialStatement._from_serializable_value(value.get("data"))
                return np.array(data, dtype=object)

            if value.get("__tuple__") is True:
                return tuple(FinancialStatement._from_serializable_value(item) for item in value.get("data", []))

            return {key: FinancialStatement._from_serializable_value(val) for key, val in value.items()}

        if isinstance(value, list):
            return [FinancialStatement._from_serializable_value(item) for item in value]

        return value

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

    def to_dict(self, include_metadata: bool = True, include_notes: bool = True) -> Dict[str, Any]:
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

    def to_ohada_json(self, indent: int = 2) -> str:
        """
        Export this statement as a structured OHADA JSON string.

        This method returns a JSON string with the rich labeled OHADA structure
        (balance_sheet.assets/liabilities, income_statement, cashflow_statement,
        per-account records with reference/label/values). This is different from
        to_json()/to_dict() which return a raw dict with simple arrays.

        Args:
            indent: JSON indentation level (default: 2)

        Returns:
            JSON string with structured OHADA format

        Example:
            >>> ohada_json_str = statement.to_ohada_json()
            >>> parsed = json.loads(ohada_json_str)
            >>> 'balance_sheet' in parsed
            True
        """
        # Lazy import to avoid circular dependency between core and formatters
        from ..formatters.json_formatter import OHADAJSONFormatter
        return OHADAJSONFormatter.to_json(self, indent=indent)

    def to_ohada_dict(self) -> Dict[str, Any]:
        """
        Export this statement as a structured OHADA dictionary.

        This method returns a dict with the rich labeled OHADA structure
        (balance_sheet.assets/liabilities, income_statement, cashflow_statement,
        per-account records with reference/label/values). This is different from
        to_dict() which returns a raw dict with simple arrays.

        Returns:
            Dictionary with structured OHADA format

        Example:
            >>> ohada_dict = statement.to_ohada_dict()
            >>> 'balance_sheet' in ohada_dict
            True
            >>> 'income_statement' in ohada_dict
            True
        """
        # Lazy import to avoid circular dependency between core and formatters
        from ..formatters.json_formatter import OHADAJSONFormatter
        return OHADAJSONFormatter.format_statement_data(self)

    def to_serializable_dict(self, include_metadata: bool = True, include_notes: bool = True) -> Dict[str, Any]:
        """
        Return a JSON-safe payload that can reconstruct this FinancialStatement.

        This is intended for persistence layers such as Redis. It stores the
        raw extracted arrays and lets xarray DataArrays be rebuilt lazily when
        the statement is loaded back.
        """
        payload = {
            "schema_version": self.SERIALIZATION_SCHEMA_VERSION,
            "assets": self._to_serializable_value(self._asset_data),
            "liabilities": self._to_serializable_value(self._liability_data),
            "income": self._to_serializable_value(self._income_data),
            "cashflow": self._to_serializable_value(self._cashflow_data),
            "other": self._to_serializable_value(self._other_data),
            "periods": self._to_serializable_value(self.periods),
            "file_path": self.file_path,
        }

        if include_metadata:
            payload["metadata"] = self._to_serializable_value(self.metadata.__dict__ if self.metadata else None)

        if include_notes:
            payload["notes"] = self._to_serializable_value(self.notes)

        return payload

    @classmethod
    def from_serializable_dict(cls, payload: Dict[str, Any]) -> "FinancialStatement":
        """
        Rebuild a FinancialStatement from to_serializable_dict() output.
        """
        metadata_payload = cls._from_serializable_value(payload.get("metadata"))
        metadata = CompanyMetadata(**metadata_payload) if metadata_payload else None

        return cls(
            _asset_data=cls._from_serializable_value(payload.get("assets")),
            _liability_data=cls._from_serializable_value(payload.get("liabilities")),
            _income_data=cls._from_serializable_value(payload.get("income")),
            _cashflow_data=cls._from_serializable_value(payload.get("cashflow")),
            _other_data=cls._from_serializable_value(payload.get("other")),
            notes=cls._from_serializable_value(payload.get("notes")),
            periods=cls._from_serializable_value(payload.get("periods")),
            file_path=payload.get("file_path"),
            metadata=metadata,
        )

    def to_json_string(self, include_metadata: bool = True, include_notes: bool = True, **json_kwargs) -> str:
        """
        Serialize this statement to a JSON string.
        """
        return json.dumps(
            self.to_serializable_dict(include_metadata=include_metadata, include_notes=include_notes),
            **json_kwargs,
        )

    @classmethod
    def from_json_string(cls, json_string: str) -> "FinancialStatement":
        """
        Rebuild a FinancialStatement from a JSON string.
        """
        return cls.from_serializable_dict(json.loads(json_string))

    def to_dataframe(
        self, statement: str = None, tidy: bool = True, value_type: str = "Net", reset_index: bool = True
    ) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Convert financial statement data to pandas DataFrame for time-series analysis.

        Args:
            statement: Name of statement to return ('asset', 'liability', 'income', 'cashflow', 'other').
                      If None, returns a dict of DataFrames for all statements.
            tidy: If True, returns long format with columns [Reference, Label, annee, value, valeur].
                  If False, returns wide format with account index and year columns.
            value_type: For assets only, which value type to use ('Gross', 'Amortissement', 'Net').
                       Ignored for other statements.
            reset_index: If True, resets the MultiIndex to columns. If False, keeps the MultiIndex (Label, Reference)
                        as the index, which is useful for hierarchical operations.

        Returns:
            Single DataFrame if statement is specified, otherwise dict of DataFrames for all statements.
            Returns None or empty DataFrame if underlying array is None.

        Examples:
            >>> # Get all statements in tidy format with MultiIndex as columns
            >>> dfs = statement.to_dataframe()
            >>> # Get single statement in wide format with MultiIndex preserved as index
            >>> income_df = statement.to_dataframe('income', tidy=False, reset_index=False)
            >>> # Get assets with Gross values
            >>> assets_gross = statement.to_dataframe('asset', value_type='Gross')
        """
        def convert_array_to_df(da: xr.DataArray, is_asset: bool = False) -> pd.DataFrame:
            """Convert xarray DataArray to pandas DataFrame."""
            if da is None:
                return pd.DataFrame()

            # For assets, select the specified value_type
            if is_asset and "valeur" in da.dims:
                da = da.sel(valeur=value_type)

            if tidy:
                # Tidy (long) format: columns [Reference, Label, annee, value]
                if is_asset and "valeur" in da.dims:
                    # Use to_dataframe() for assets with valeur dimension
                    df = da.to_dataframe()
                    if reset_index:
                        df = df.reset_index()
                else:
                    # Use to_pandas() for other statements (2D arrays), then melt to tidy format
                    df = da.to_pandas()
                    if reset_index:
                        df = df.reset_index()
                        # Melt so years become values in annee column
                        id_vars = ["Label", "Reference"]
                        value_vars = [col for col in df.columns if col not in id_vars]
                        df = df.melt(id_vars=id_vars, value_vars=value_vars, var_name="annee", value_name="value")
                        # Convert annee to datetime
                        df["annee"] = pd.to_datetime(df["annee"])
                    else:
                        # Keep MultiIndex, melt with index as id_vars
                        df = df.reset_index()
                        id_vars = ["Label", "Reference"]
                        value_vars = [col for col in df.columns if col not in id_vars]
                        df = df.melt(id_vars=id_vars, value_vars=value_vars, var_name="annee", value_name="value")
                        # Convert annee to datetime
                        df["annee"] = pd.to_datetime(df["annee"])
                        # Set MultiIndex back
                        df = df.set_index(["Label", "Reference"])
            else:
                # Wide format: index = account, columns = years
                df = da.to_pandas()
                if reset_index:
                    # Reset index to make Label and Reference columns
                    df = df.reset_index()

            # Ensure time axis is monotonic increasing
            if "annee" in df.columns:
                df = df.sort_values("annee")

            return df

        # Handle single statement request
        if statement is not None:
            if statement not in self.arrays:
                raise ValueError(
                    f"Invalid statement '{statement}'. Must be one of: {list(self.arrays.keys())}"
                )

            da = self.arrays[statement]
            is_asset = (statement == "asset")
            return convert_array_to_df(da, is_asset)

        # Return all statements as dict
        result = {}
        for stmt_name, da in self.arrays.items():
            is_asset = (stmt_name == "asset")
            result[stmt_name] = convert_array_to_df(da, is_asset)

        return result

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

    def get_other(self, reference: str) -> xr.DataArray:
        """Query your other data natively via reference code."""
        # This searches your MultiIndex 'compte' seamlessly
        return self.other.sel(Reference=reference)

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

        for _key, entry in self.notes.items():
            if entry.get("name", "").strip().lower() == name:
                return entry.get("preprocess_value") if processed else entry.get("raw_value")

        return None

    def plot(self, *args, **kwargs):
        from ohada_extractor.visualization.base_plotter import plot_router

        plot_router(self, *args, **kwargs)
