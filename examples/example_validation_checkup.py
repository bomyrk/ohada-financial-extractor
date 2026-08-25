"""
Example: Run a detailed OHADA coherence validation checkup.

This example uses the bundled DSF sample and produces:
- high-level statement check results
- individual OHADA relationship results
- expected and actual values by period
- JSON export of the validation report
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from ohada_extractor import FinancialExtractor


def collect_numeric_values(value: Any) -> list[float]:
    if isinstance(value, dict):
        values = []
        for nested_value in value.values():
            values.extend(collect_numeric_values(nested_value))
        return values

    if value is None:
        return []

    number = float(value)
    if np.isnan(number):
        return []
    return [number]


def print_report(report_dict: dict) -> None:
    summary = report_dict["summary"]

    print("\nValidation summary")
    print("-" * 40)
    print(f"File:          {report_dict['file_path']}")
    print(f"Periods:       {', '.join(report_dict['periods'])}")
    print(f"Total checks:  {summary['total_checks']}")
    print(f"Passed:        {summary['passed_checks']}")
    print(f"Failed:        {summary['failed_checks']}")
    print(f"Quality score: {summary['data_quality_score']:.2f}/100")
    print(f"Overall:       {'PASS' if summary['passed'] else 'FAIL'}")

    print("\nDetailed results")
    print("-" * 110)
    print(f"{'Result':<8} {'Check':<42} {'Expression':<32} {'Max absolute difference':>24}")
    print("-" * 110)

    for check in report_dict["checks"]:
        result = "PASS" if check["passed"] else "FAIL"
        differences = [abs(value) for value in collect_numeric_values(check.get("difference", {}))]
        max_diff = max(differences) if differences else 0.0
        name = check["name"][:39] + "..." if len(check["name"]) > 42 else check["name"]
        expression = check["expression"][:29] + "..." if len(check["expression"]) > 32 else check["expression"]
        print(f"{result:<8} {name:<42} {expression:<32} {max_diff:>24,.2f}")

    failed = [check for check in report_dict["checks"] if not check["passed"]]
    if failed:
        print("\nFailed check details")
        print("-" * 80)
        for check in failed:
            print(f"\n{check['name']} ({check['expression']})")
            for period, actual in check.get("actual", {}).items():
                expected = check["expected"][period]
                diff = check["difference"][period]
                print(f"  {period}: actual={actual} expected={expected} difference={diff}")


def main() -> None:
    sample_file = Path(__file__).parent / "data" / "DSF_Normal_Tantanpion_2024.xlsx"
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    if not sample_file.exists():
        print(f"Error: sample file not found at {sample_file}")
        return

    print(f"Running validation checkup for: {sample_file}")
    statement = FinancialExtractor().extract_from_excel(sample_file)

    report = statement.build_coherence_report()
    report_dict = report.to_dict()

    print_report(report_dict)

    output_path = output_dir / "validation_checkup_report.json"
    output_path.write_text(json.dumps(report_dict, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nValidation report saved to: {output_path}")


if __name__ == "__main__":
    main()
