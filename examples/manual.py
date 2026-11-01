from src.ohada_extractor import FinancialExtractor

extractor = FinancialExtractor()
data = extractor.extract_from_directory("examples/data")

data.get_note("note21", processed=False)
sorted(data.notes.keys())

data.to_ohada_dict()
extractor._raw_data.keys()
extractor._raw_data["assets"]