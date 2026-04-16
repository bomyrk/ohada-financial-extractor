"""
Internal coherence validation for OHADA financial statements.

This module converts extracted numpy arrays into xarray DataArrays
and validates:
- balance sheet equality (assets = liabilities)
- income statement consistency
- cashflow consistency
- predefined financial relationships (AD = AE + AF + ...)
"""

from __future__ import annotations
import logging
import numpy as np
import pandas as pd
import xarray as xr
import re

from typing import List, Tuple

from xarray import DataArray

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
#  RELATIONSHIP DEFINITIONS
# ----------------------------------------------------------------------

def define_relationships() -> List[Tuple[str, str]]:
    """
    Define all financial relationships to validate.
    Each tuple is (expression, financial_type).
    """
    return [
        ("AD=AE+AF+AG+AH", "asset"),
        ("AI=AJ+AK+AL+AM+AN", "asset"),
        ("AQ=AR+AS", "asset"),
        ("AZ=AD+AI+AP+AQ", "asset"),
        ("BC=BH+BI+BJ", "asset"),
        ("BK=BA+BB+BC", "asset"),
        ("BT=BQ+BR+BS", "asset"),
        ("BZ=AZ+BK+BT+BU", "asset"),

        ("CP=CA+CB+CD+CE+CF+CG+CH+CJ+CL+CM", "liability"),
        ("DD=DA+DB+DC", "liability"),
        ("DF=CP+DD", "liability"),
        ("DP=DH+DI+DJ+DK+DM+DN", "liability"),
        ("DT=DQ+DR", "liability"),
        ("DZ=DF+DP+DT+DY", "liability"),

        ("XA=TA+RA+RB", "income"),
        ("XB=TA+TB+TC+TD", "income"),
        ("XC=XB+RA+RB+TE+TF+TG+TH+TI+RC+RD+RE+RF+RG+RH+RI+RJ", "income"),
        ("XD=XC+RK", "income"),
        ("XE=XD+TJ+RL", "income"),
        ("XF=TK+TL+TM-RM-RN", "income"),
        ("XG=XE+XF", "income"),
        ("XH=TN+TO-RO-RP", "income"),
        ("XI=XG+XH+RQ+RS", "income"),

        ("ZB=FA-FB-FC-FD+FE", "cashflow"),
        ("ZC=FI+FJ-FF-FG-FH", "cashflow"),
        ("ZD=FK+FL-FM-FN", "cashflow"),
        ("ZE=FO+FP+FQ", "cashflow"),
        ("ZF=ZD+ZE", "cashflow"),
    ]


# ----------------------------------------------------------------------
#  RELATION CLASS
# ----------------------------------------------------------------------

class Relation:
    """
    Represents a financial relationship between accounts.
    Example: "AD = AE + AF + AG"
    """

    def __init__(self, expression: str, financial_type: str, data: xr.DataArray):
        self.expression = expression
        self.financial_type = financial_type
        self.left_side, self.right_side = self.parse_expression(expression)
        self.data = data

    @staticmethod
    def parse_expression(expression: str) -> tuple:
        left, right = expression.split("=")
        return left.strip(), right.strip()

    def compute_sum(self, side: str, op_hdl: bool = False) -> DataArray | None:
        """
        Compute the sum of accounts on one side of the expression.
        Handles + and - operators.
        """
        expr = getattr(self, f"{side}_side")
        tokens = re.split(r'([+-])', expr.replace(" ", "")) if op_hdl else re.split(r'[+-]', expr.replace(" ", ""))

        total = 0
        sign = 1

        if op_hdl:
            for token in tokens:
                if token == "+":
                    sign = 1
                elif token == "-":
                    sign = -1
                elif token:
                    try:
                        if self.financial_type == "asset":
                            # 3D: (compte, annee, valeur) → select Net
                            values = self.data.sel(compte=pd.IndexSlice[:, token], valeur="Net").drop_vars("compte")
                        else:
                            # 2D: (compte, annee)
                            values = self.data.sel(compte=pd.IndexSlice[:, token]).drop_vars("compte")

                        contrib = sign * values
                        total = contrib if total is None else total + contrib

                    except KeyError:
                        logger.error(
                            f"Unknown account reference '{token}' in expression '{self.expression}' "
                            f"for type '{self.financial_type}'"
                        )
        else:
            try:

                values = self.data.sel(compte=pd.IndexSlice[:, tokens])

            except KeyError:
                logger.error(
                    f"Unknown account reference '{tokens}' in expression '{self.expression}' "
                    f"for type '{self.financial_type}'"
                )
            # Sum over 'compte', keep per-year values, ignore NaNs
            return values.sum(dim="compte", skipna=True)

    def verify(self) -> bool:
        left_total = self.compute_sum("left")
        right_total = self.compute_sum("right")

        if not np.allclose(left_total, right_total):
            logger.error(
                f" - Validation failed: "
                f"{self.left_side} ({left_total}) ≠ {self.right_side} ({right_total}) "
                f"for {self.financial_type}"
            )
            return False

        return True


# ----------------------------------------------------------------------
#  MAIN VALIDATOR CLASS
# ----------------------------------------------------------------------

class CoherenceValidator:
    """
    Validates internal coherence of OHADA financial statements using xarray.
    """

    def __init__(self, asset, liability, income, cashflow, periods):
        self.asset = asset
        self.liability = liability
        self.income = income
        self.cashflow = cashflow
        self.periods = periods

        self.relations = [
            Relation(expr, ftype, getattr(self, ftype))
            for expr, ftype in define_relationships()
        ]

    # ---------------------------------------------------------
    #  FACTORY METHOD
    # ---------------------------------------------------------
    @staticmethod
    def from_financial_statement(statement):
        """
        Build a validator from a FinancialStatement object.
        Converts numpy arrays into xarray DataArrays.
        """

        # Build MultiIndex accounts
        from ohada_extractor.core.schemas import (
            ASSETS_ACCOUNTS,
            LIABILITIES_ACCOUNTS,
            INCOME_ACCOUNTS,
            CASHFLOW_ACCOUNTS,
        )

        def create_index(data):
            return pd.MultiIndex.from_tuples(data, names=["Label", "Reference"])

        asset_idx = create_index(ASSETS_ACCOUNTS)
        liab_idx = create_index(LIABILITIES_ACCOUNTS)
        income_idx = create_index(INCOME_ACCOUNTS)
        cash_idx = create_index(CASHFLOW_ACCOUNTS)

        n_years = len(statement.periods)
        years = pd.Index(statement.periods, name="annee") if n_years > 2 else pd.Index(statement.periods[::-1], name="annee")

        # ---------------------------------------------------------
        # Helper to reshape data into (account, year, value_type)
        # ---------------------------------------------------------
        def reshape_statement(data, value_types):
            """
            data: numpy array with first column = reference
            value_types: list of value type names (e.g., ["Net"] or ["Gross","Amort","Net"])
            """
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

            # Reshape into (account, year, value_type)
            reshaped = values.reshape(values.shape[0], n_years, n_types) if n_types > 1 else values
            return reshaped

        # ---------------------------------------------------------
        # Build xarray DataArrays
        # ---------------------------------------------------------
        asset_xr = xr.DataArray(
            data=reshape_statement(statement.asset_data, ["Gross", "Amortissement", "Net"]),
            coords={"compte": asset_idx, "annee": years, "valeur": ["Gross", "Amortissement", "Net"]},
            dims=("compte", "annee", "valeur"),
            name="asset"
        ).astype(float).round(2)

        liab_xr = xr.DataArray(
            data=reshape_statement(statement.liability_data, ["Net"]),
            coords={"compte": liab_idx, "annee": years},
            dims=("compte", "annee"),
            name="liabilities"
        ).astype(float).round(2)

        income_xr = xr.DataArray(
            data=reshape_statement(statement.income_data, ["Net"]),
            coords={"compte": income_idx, "annee": years},
            dims=("compte", "annee"),
            name="income"
        ).astype(float).round(2)

        cash_xr = xr.DataArray(
            data=reshape_statement(statement.cashflow_data, ["Net"]),
            coords={"compte": cash_idx, "annee": years},
            dims=("compte", "annee"),
            name="cashflow"
        ).astype(float).round(2)

        return CoherenceValidator(asset_xr, liab_xr, income_xr, cash_xr, years)

    # ---------------------------------------------------------
    #  VALIDATION METHODS
    # ---------------------------------------------------------

    def validate_balance_sheet(self) -> bool:
        total_assets = self.asset.sel(compte=pd.IndexSlice[:, "BZ"], valeur="Net")
        total_liabilities = self.liability.sel(compte=pd.IndexSlice[:, "DZ"])

        valid = np.allclose(total_assets, total_liabilities)

        if not valid:
            logger.error(
                f" Balance sheet validation failed: "
                f"Assets (BZ) ≠ Liabilities (DZ)"
            )

        return valid

    def validate_income_statement(self) -> bool:
        net_income = self.income.sel(compte=pd.IndexSlice[:, "XI"])
        net_income_report_liabilities = self.liability.sel(compte=pd.IndexSlice[:, "CJ"])

        valid = np.allclose(net_income, net_income_report_liabilities)

        if not valid:
            logger.error(
                f" Income statement validation failed: "
                f"Net income (XI) ≠ Net income reported (CJ)"
            )

        return valid

    def validate_cash_flow_statement(self) -> bool:
        net_cash_flow = self.cashflow.sel(compte=pd.IndexSlice[:, "ZG"])
        expected = (
            self.cashflow.sel(compte=pd.IndexSlice[:, "ZB"]) +
            self.cashflow.sel(compte=pd.IndexSlice[:, "ZC"]) +
            self.cashflow.sel(compte=pd.IndexSlice[:, "ZF"])
        )

        valid = np.allclose(net_cash_flow, expected)

        if not valid:
            logger.error(
                f" Cash flow validation failed: "
                f"ZG ≠ ZB + ZC + ZF"
            )

        return valid

    def validate_all_relationships(self) -> bool:
        results = [rel.verify() for rel in self.relations]
        if not all(results):
            logger.error(f" Financial relationship validation failed.")
        return all(results)

    def validate(self) -> bool:
        """
        Run all validation checks.
        """
        checks = [
            self.validate_balance_sheet(),
            self.validate_income_statement(),
            self.validate_cash_flow_statement(),
            self.validate_all_relationships(),
        ]

        if not all(checks):
            logger.error(f" Financial statement coherence check FAILED.")
            return False

        logger.info(f" All financial statement coherence checks PASSED.")
        return True
