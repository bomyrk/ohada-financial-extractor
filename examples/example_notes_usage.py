"""
Example: Extracting and Using OHADA Notes (Annexes)
===================================================

This example demonstrates how to:

1. Load a DSF Excel file
2. Run the FinancialExtractor
3. Extract OHADA notes (annexes)
4. Retrieve notes by key or by human-readable name
5. Inspect raw and preprocessed values
6. Export notes to JSON

Run:
    python examples/example_notes_usage.py
"""

from pathlib import Path
import json
import os

from ohada_extractor.core.extractor import FinancialExtractor


def to_python_value(value):
    """Convert numpy values to JSON‑friendly Python types."""
    import numpy as np

    if isinstance(value, np.ndarray):
        if value.size == 1:
            return value.item()
        return value.tolist()

    if isinstance(value, np.generic):
        return value.item()

    return value


def main():

    # -------------------------------------------------------------------
    # 1. Load a DSF Excel file
    # -------------------------------------------------------------------

    sample_file = Path(__file__).parent / 'data' / 'DSF_Normal_Tantanpion_2024.xlsx'

    extractor = FinancialExtractor()

    print("\n--- Extracting statement from DSF Excel file ---")
    statement = extractor.extract_from_excel(sample_file)

    # Build xarray (recommended)
    statement.to_xarray()

    print(f"Extracted {len(statement.notes)} notes.")


    # -------------------------------------------------------------------
    # 3. Retrieve a note by key
    # -------------------------------------------------------------------

    print("\n--- Example: Retrieve NOTE 3A by key ---")

    note_key = "note3a"  # adjust to your actual key names
    note_raw = statement.get_note(note_key)
    note_pre = statement.get_note(note_key, processed=True)

    print(f"Note key: {note_key}")
    print("Raw value:")
    print(note_raw)
    print("\nPreprocessed value:")
    print(note_pre)


    # -------------------------------------------------------------------
    # 4. Retrieve a note by human-readable name
    # -------------------------------------------------------------------

    print("\n--- Example: Retrieve note by name ---")

    note_name = "IMMOBILISATION BRUTE"  # example name
    note_by_name = statement.get_note_by_name(note_name)

    print(f"Searching for note named: {note_name}")
    print("Result:")
    print(note_by_name)


    # -------------------------------------------------------------------
    # 5. Export all notes to JSON
    # -------------------------------------------------------------------

    print("\n--- Exporting all notes to JSON ---")

    notes_export = {}

    for key, entry in statement.notes.items():
        notes_export[key] = {
            "name": entry.get("name"),
            "raw_value": to_python_value(entry.get("raw_value")),
            "preprocess_value": to_python_value(entry.get("preprocess_value")),
        }

    notes_json = json.dumps(notes_export, indent=4, ensure_ascii=False)

    print(notes_json)

    os.makedirs("output", exist_ok=True)
    output_path = sample_file.parent.parent / "output"/ "notes_export.json"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(notes_json)

    print(f"\nNotes exported to: {output_path}")


if __name__ == "__main__":
    main()
