"""
Example: Extract and inspect company metadata from an OHADA DSF file.

This example uses the bundled DSF sample and demonstrates:
- base company characteristics from Fiche R2
- KPI extraction from Note 31
- activity breakdown, main activity, and secondary activities
- year-over-year activity growth and sector concentration
- JSON export of the metadata object
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from ohada_extractor import FinancialExtractor


def to_python_value(value: Any) -> Any:
    """Convert NumPy-heavy metadata values into JSON-friendly Python values."""
    if isinstance(value, np.ndarray):
        if value.size == 1:
            return value.item()
        return value.tolist()

    if isinstance(value, np.generic):
        return value.item()

    if isinstance(value, dict):
        return {to_python_value(k): to_python_value(v) for k, v in value.items()}

    if isinstance(value, list):
        return [to_python_value(item) for item in value]

    return value


def format_money(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):,.0f}"


def print_activity_table(activities: list[dict], limit: int = 8) -> None:
    print("\nLatest activity breakdown")
    print("-" * 86)
    print(f"{'Rank':<5} {'Ref':<8} {'Activity':<38} {'Value':>16} {'Share':>10}")
    print("-" * 86)

    for rank, activity in enumerate(activities[:limit], start=1):
        label = activity.get("label") or "Activity"
        label = label[:35] + "..." if len(label) > 38 else label
        print(
            f"{rank:<5} "
            f"{activity.get('reference', ''):<8} "
            f"{label:<38} "
            f"{format_money(activity.get('value')):>16} "
            f"{activity.get('percentage', 0):>9.2f}%"
        )


def print_yoy_growth(yoy_growth: dict[int, list[dict]]) -> None:
    if not yoy_growth:
        print("\nYear-over-year activity growth: not available for a single activity period.")
        return

    print("\nYear-over-year activity growth")
    print("-" * 100)
    print(f"{'Period':<8} {'Ref':<8} {'Activity':<34} {'Previous':>14} {'Current':>14} {'Growth':>10} {'Trend':>12}")
    print("-" * 100)

    for period_idx, rows in sorted(yoy_growth.items()):
        for row in rows:
            label = row.get("label") or "Activity"
            label = label[:31] + "..." if len(label) > 34 else label
            growth = row.get("yoy_growth")
            growth_text = "n/a" if growth is None else f"{growth:.2f}%"
            print(
                f"{period_idx:<8} "
                f"{row.get('reference', ''):<8} "
                f"{label:<34} "
                f"{format_money(row.get('value_prev')):>14} "
                f"{format_money(row.get('value_curr')):>14} "
                f"{growth_text:>10} "
                f"{row.get('trend') or 'n/a':>12}"
            )


def main() -> None:
    sample_file = Path(__file__).parent / "data" / "DSF_Normal_Tantanpion_2024.xlsx"
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    if not sample_file.exists():
        print(f"Error: sample file not found at {sample_file}")
        return

    print(f"Extracting metadata from: {sample_file}")
    statement = FinancialExtractor().extract_from_excel(sample_file)
    metadata = statement.build_metadata()
    if metadata is None:
        raise RuntimeError("Metadata extraction failed. Fiche R2 metadata was not found.")

    print("\nCompany profile")
    print("-" * 40)
    print(f"Legal form:        {metadata.legal_form}")
    print(f"Country:           {metadata.country}")
    print(f"Currency:          {metadata.currency}")
    print(f"Fiscal regime:     {metadata.regime_fiscal}")
    print(f"Year of creation:  {metadata.year_creation}")
    print(f"Units/sites:        {metadata.number_of_units}")
    print(f"Ownership:         {metadata.owned}")

    print("\nNote 31 KPIs")
    print("-" * 40)
    print(f"Dividend by period:       {to_python_value(metadata.dividend)}")
    print(f"Shares by period:         {to_python_value(metadata.number_of_shares)}")
    print(f"Employees by period:      {to_python_value(metadata.number_of_employees)}")

    if metadata.main_activity:
        print("\nMain activity")
        print("-" * 40)
        print(f"Reference:   {metadata.main_activity.get('reference')}")
        print(f"Label:       {metadata.main_activity.get('label')}")
        print(f"Value:       {format_money(metadata.main_activity.get('value'))}")
        print(f"Share:       {metadata.main_activity.get('percentage', 0):.2f}%")

    if metadata.activities_breakdown:
        print_activity_table(metadata.activities_breakdown)

    if metadata.sector_concentration:
        print("\nSector concentration by extracted period")
        print("-" * 40)
        for period_idx, hhi in sorted(metadata.sector_concentration.items()):
            print(f"Period {period_idx}: HHI={hhi:.2f}")

    print_yoy_growth(metadata.yoy_growth or {})

    missing = metadata.missing_fields()
    print("\nMissing metadata fields")
    print("-" * 40)
    if missing:
        for field in missing:
            print(f"- {field}")
    else:
        print("None")

    metadata_dict = {field: to_python_value(value) for field, value in metadata.__dict__.items()}
    output_path = output_dir / "company_metadata.json"
    output_path.write_text(json.dumps(metadata_dict, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nMetadata JSON saved to: {output_path}")


if __name__ == "__main__":
    main()
