# Changelog
All notable changes to this project will be documented in this file.

The format is based on **Keep a Changelog**  
and this project adheres to **Semantic Versioning**.

## [Unreleased]

## [1.0.4] - 2026-11-06
### Added
- Fiche R1 extraction (`FinancialExtractor._process_fiche_r1`) covering fiscal period, registry, activity, company identity and contact fields (`R1_FIELDS`).
- `CompanyMetadataExtractor.from_fiche_r1` and new `CompanyMetadata` fields populated from Fiche R1 (sigle, address, city, phone, email, postal code/box, activity label, importer code, fiscal year start/end).
- Note schemas for Fiche R1 and Notes 14, 15A, 15B, 20–27, 31, 32, 33 and 34.
- Mapping-style access on `FinancialStatement` (`keys`, `__getitem__`, `__contains__`, `__iter__`, `__len__`).

### Changed
- JSON formatter exports the new company metadata fields.
- Example outputs are no longer shipped in the source distribution.

## [0.1.2] - 2026-05-02
### Fixed
- Corrected PyPI project description by properly including README from docs/.
- Updated MANIFEST.in to include documentation files.

### Changed
- Improved README badge section for a more professional presentation.

## [0.1.1] - 2026-05-01
### Fixed
- Packaging metadata issues preventing PyPI description from rendering.

## [0.1.0] - 2026-04-30
### Added
- Initial stable release of the OHADA Financial Extractor.
