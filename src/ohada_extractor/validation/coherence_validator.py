"""
Internal coherence validation for OHADA financial statements.

This module validates:
- balance sheet equality (assets = liabilities)
- income statement consistency
- cashflow consistency
- predefined financial relationships (AD = AE + AF + ...)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, List, Tuple

import numpy as np
import pandas as pd
import xarray as xr

logger = logging.getLogger(__name__)


@dataclass
class CoherenceCheckResult:
    """
    Detailed result for one coherence check.

    The actual/expected/difference mappings are intentionally generic so they
    can represent both scalar statements and asset values split by Gross,
    Amortissement, and Net.
    """

    name: str
    expression: str
    financial_type: str
    passed: bool
    actual: dict[str, Any] = field(default_factory=dict)
    expected: dict[str, Any] = field(default_factory=dict)
    difference: dict[str, Any] = field(default_factory=dict)
    value_labels: list[str] = field(default_factory=lambda: ["value"])
    severity: str = "medium"
    message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the check result."""
        return {
            "name": self.name,
            "expression": self.expression,
            "financial_type": self.financial_type,
            "passed": self.passed,
            "severity": self.severity,
            "value_labels": self.value_labels,
            "actual": self.actual,
            "expected": self.expected,
            "difference": self.difference,
            "message": self.message,
        }

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return (
            "CoherenceCheckResult("
            f"{status}, "
            f"name={self.name}, "
            f"expression={self.expression}, "
            f"type={self.financial_type}, "
            f"severity={self.severity}"
            ")"
        )


@dataclass
class CoherenceReport:
    """
    Aggregated coherence report for a financial statement.
    """

    file_path: str | None = None
    periods: list[str] = field(default_factory=list)
    checks: list[CoherenceCheckResult] = field(default_factory=list)

    @property
    def total_checks(self) -> int:
        return len(self.checks)

    @property
    def passed_checks(self) -> int:
        return sum(1 for check in self.checks if check.passed)

    @property
    def failed_checks(self) -> int:
        return self.total_checks - self.passed_checks

    @property
    def passed(self) -> bool:
        return self.failed_checks == 0

    @property
    def all_checks_passed(self) -> bool:
        return self.passed

    @property
    def data_quality_score(self) -> float:
        """
        Simple transparent score from 0 to 100.

        A later version can weight high-severity checks more strongly.
        """
        if self.total_checks == 0:
            return 0.0
        return round((self.passed_checks / self.total_checks) * 100, 2)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the report."""
        return {
            "file_path": self.file_path,
            "periods": self.periods,
            "summary": {
                "passed": self.passed,
                "data_quality_score": self.data_quality_score,
                "total_checks": self.total_checks,
                "passed_checks": self.passed_checks,
                "failed_checks": self.failed_checks,
            },
            "checks": [check.to_dict() for check in self.checks],
        }

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return (
            "CoherenceReport("
            f"{status}, "
            f"score={self.data_quality_score:.2f}/100, "
            f"checks={self.passed_checks}/{self.total_checks}, "
            f"file_path={self.file_path or 'n/a'}"
            ")"
        )


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

    def __str__(self) -> str:
        return f"Relation(type={self.financial_type}, expression={self.expression})"

    def compute_sum(self, side: str) -> xr.DataArray | None:
        """
        Compute one side of the expression, preserving + and - operators.
        """
        expr = getattr(self, f"{side}_side")

        accounts = [account.strip() for account in expr.replace(" ", "").replace("-", "+").split("+")]
        account_values = self.data.sel(compte=pd.IndexSlice[:, accounts])

        return account_values.sum(dim="compte", skipna=True, min_count=1)

    def verify(self) -> bool:
        left_total = self.compute_sum("left")
        right_total = self.compute_sum("right")

        if left_total is None or right_total is None:
            return False

        if not np.allclose(left_total, right_total, equal_nan=True):
            logger.error(
                f" - Validation failed: "
                f"{self.left_side} ({left_total}) != {self.right_side} ({right_total}) "
                f"for {self.financial_type}"
            )
            return False

        return True


class CoherenceValidator:
    """
    Validates internal coherence of OHADA financial statements using xarray.
    """

    def __init__(self, asset, liability, income, cashflow, periods, file_path: str | None = None):
        self.asset = asset
        self.liability = liability
        self.income = income
        self.cashflow = cashflow
        self.periods = periods
        self.file_path = file_path
        self.relations = [Relation(expr, ftype, getattr(self, ftype)) for expr, ftype in define_relationships()]

    @staticmethod
    def from_financial_statement(statement):
        """
        Build a validator from a FinancialStatement object.
        Reuses the statement's lazily-built xarray DataArrays.
        """
        arrays = statement.arrays
        years = arrays["asset"].coords["annee"].to_index()
        return CoherenceValidator(
            arrays["asset"],
            arrays["liability"],
            arrays["income"],
            arrays["cashflow"],
            years,
            file_path=statement.file_path,
        )

    @staticmethod
    def _to_python_value(value: Any) -> Any:
        """Convert pandas, xarray, and NumPy values into JSON-friendly values."""
        if isinstance(value, xr.DataArray):
            return CoherenceValidator._to_python_value(value.values)

        if isinstance(value, np.ndarray):
            return [CoherenceValidator._to_python_value(item) for item in value.tolist()]

        if isinstance(value, np.generic):
            return CoherenceValidator._to_python_value(value.item())

        if isinstance(value, float) and np.isnan(value):
            return None

        if isinstance(value, pd.Timestamp):
            return value.date().isoformat()

        if isinstance(value, dict):
            return {
                str(CoherenceValidator._to_python_value(k)): CoherenceValidator._to_python_value(v)
                for k, v in value.items()
            }

        if isinstance(value, list):
            return [CoherenceValidator._to_python_value(item) for item in value]

        return value

    def _values_matrix(self, data: xr.DataArray) -> tuple[np.ndarray, list[str]]:
        """
        Return values as (period, value_type), preserving asset value types.

        Assets carry Gross, Amortissement, and Net values. Other statements
        carry one scalar value per period.
        """
        value_labels = ["valeur"]

        if "valeur" in data.dims:
            value_labels = [str(label) for label in data.coords["valeur"].values]
            ordered = data.transpose("annee", "valeur", ...)
        else:
            ordered = data.transpose("annee", ...)

        values = np.asarray(ordered.values, dtype=float).reshape(len(self.periods), -1)
        return values, value_labels

    def _values_by_period(self, values: np.ndarray, value_labels: list[str]) -> dict[str, Any]:
        result = {}

        for idx, period in enumerate(self.periods):
            row = values[idx]
            period_key = self._to_python_value(period)

            if len(value_labels) == 1:
                result[period_key] = self._to_python_value(row[0])
            else:
                result[period_key] = {
                    label: self._to_python_value(row[value_idx]) for value_idx, label in enumerate(value_labels)
                }

        return result

    def _build_check_result(
        self,
        name: str,
        expression: str,
        financial_type: str,
        actual: xr.DataArray,
        expected: xr.DataArray,
        severity: str = "medium",
    ) -> CoherenceCheckResult:
        actual_values, value_labels = self._values_matrix(actual)
        expected_values, expected_labels = self._values_matrix(expected)

        if expected_labels != value_labels:
            raise ValueError(
                f"Cannot compare '{name}': actual value labels {value_labels} "
                f"do not match expected value labels {expected_labels}."
            )

        difference = actual_values - expected_values
        passed = bool(np.allclose(actual_values, expected_values, equal_nan=True))

        return CoherenceCheckResult(
            name=name,
            expression=expression,
            financial_type=financial_type,
            passed=passed,
            severity=severity,
            value_labels=value_labels,
            actual=self._values_by_period(actual_values, value_labels),
            expected=self._values_by_period(expected_values, value_labels),
            difference=self._values_by_period(difference, value_labels),
        )

    def build_report(self, file_path: str | None = None) -> CoherenceReport:
        """
        Build a detailed coherence report with statement and relationship checks.
        """
        checks = [
            self._build_check_result(
                name="Balance sheet equality",
                expression="Assets BZ = Liabilities DZ",
                financial_type="balance_sheet",
                actual=self.asset.sel(compte=pd.IndexSlice[:, "BZ"], valeur="Net"),
                expected=self.liability.sel(compte=pd.IndexSlice[:, "DZ"]),
                severity="high",
            ),
            self._build_check_result(
                name="Net income cross-check",
                expression="Income XI = Liability CJ",
                financial_type="income_statement",
                actual=self.income.sel(compte=pd.IndexSlice[:, "XI"]),
                expected=self.liability.sel(compte=pd.IndexSlice[:, "CJ"]),
                severity="high",
            ),
            self._build_check_result(
                name="Cashflow net movement",
                expression="Cashflow ZG = ZB + ZC + ZF",
                financial_type="cashflow_statement",
                actual=self.cashflow.sel(compte=pd.IndexSlice[:, "ZG"]),
                expected=self.cashflow.sel(compte=pd.IndexSlice[:, ["ZB", "ZC", "ZF"]]).sum(dim="compte", keepdims=True),
                severity="high",
            ),
        ]

        for relation in self.relations:
            actual = relation.compute_sum("left")
            expected = relation.compute_sum("right")

            if actual is None or expected is None:
                checks.append(
                    CoherenceCheckResult(
                        name=f"{relation.financial_type}: {relation.expression}",
                        expression=relation.expression,
                        financial_type=relation.financial_type,
                        passed=False,
                        severity="medium",
                        message="A referenced account was not found.",
                    )
                )
                continue

            checks.append(
                self._build_check_result(
                    name=f"{relation.financial_type}: {relation.expression}",
                    expression=relation.expression,
                    financial_type=relation.financial_type,
                    actual=actual,
                    expected=expected,
                )
            )

        return CoherenceReport(
            file_path=file_path if file_path is not None else self.file_path,
            periods=[self._to_python_value(period) for period in self.periods],
            checks=checks,
        )

    def validate_balance_sheet(self) -> bool:
        total_assets = self.asset.sel(compte=pd.IndexSlice[:, "BZ"], valeur="Net")
        total_liabilities = self.liability.sel(compte=pd.IndexSlice[:, "DZ"])

        valid = np.allclose(total_assets, total_liabilities, equal_nan=True)

        if not valid:
            logger.error("Balance sheet validation failed: Assets (BZ) != Liabilities (DZ)")

        return valid

    def validate_income_statement(self) -> bool:
        net_income = self.income.sel(compte=pd.IndexSlice[:, "XI"])
        net_income_report_liabilities = self.liability.sel(compte=pd.IndexSlice[:, "CJ"])

        valid = np.allclose(net_income, net_income_report_liabilities, equal_nan=True)

        if not valid:
            logger.error("Income statement validation failed: Net income (XI) != Net income reported (CJ)")

        return valid

    def validate_cash_flow_statement(self) -> bool:
        net_cash_flow = self.cashflow.sel(compte=pd.IndexSlice[:, "ZG"])
        expected = (
            self.cashflow.sel(compte=pd.IndexSlice[:, "ZB"])
            + self.cashflow.sel(compte=pd.IndexSlice[:, "ZC"])
            + self.cashflow.sel(compte=pd.IndexSlice[:, "ZF"])
        )

        valid = np.allclose(net_cash_flow, expected, equal_nan=True)

        if not valid:
            logger.error("Cash flow validation failed: ZG != ZB + ZC + ZF")

        return valid

    def validate_all_relationships(self) -> bool:
        results = [rel.verify() for rel in self.relations]
        if not all(results):
            logger.error("Financial relationship validation failed.")
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
            logger.error("Financial statement coherence check FAILED.")
            return False

        logger.info("All financial statement coherence checks PASSED.")
        return True
