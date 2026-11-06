from src.ohada_extractor import FinancialExtractor

extractor = FinancialExtractor()
data = extractor.extract_from_directory("examples/data")

data.get_note("note21", processed=False)
data.get_note("note21", processed=True)
sorted(data.notes.keys())

data.to_ohada_dict()
extractor._raw_data.keys()
extractor._raw_data["assets"]
data.income
data.build_metadata()
rec = data.to_ohada_json()
with open("output_path", "w", encoding="utf-8") as f:
        f.write(rec)


import json
from pathlib import Path

from ohada_extractor import FinancialExtractor
from ohada_extractor.formatters import OHADAJSONFormatter

sample_file = "examples/data/DSF_Normal_Tantanpion_2025.xlsx"
# Initialize extractor
extractor = FinancialExtractor()

# Extract data
statement = extractor.extract_from_excel(sample_file)
statement.build_metadata()
statement.asset
statement.get_note('ficher1', False)
extractor._extract_sheet_data(
    "BILAN PAYSAGE",
    "AD",
    "BZ",
    29,
    (0, 3, 4, 5, 6),

)

import openpyxl

test = openpyxl.load_workbook(sample_file, data_only=True)
test_2 = openpyxl.load_workbook(sample_file)

test.worksheets

sheet = test["BILAN PAYSAGE"]

for row in sheet.iter_rows(values_only=True):
    print(row)

wb = openpyxl.load_workbook(sample_file, data_only=True)  
print(wb.sheetnames)  
sheet = wb["BILAN PAYSAGE"]  
row = [r for r in sheet.iter_rows(values_only=True) if str(r[0]).strip() == "AM"][0]  
print(row[3:7])   # file says: (56824570, 50691190, 6133380, 2289117)