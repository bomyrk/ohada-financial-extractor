"""
Main OHADA Financial Data Extractor

Handles Excel file parsing and financial data extraction according to
OHADA accounting standards.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union
import numpy as np
import openpyxl
from dateutil.relativedelta import relativedelta
from openpyxl.worksheet.worksheet import Worksheet

from .schemas import OHADA_STATEMENTS, ASSETS_ACCOUNTS, LIABILITIES_ACCOUNTS, INCOME_ACCOUNTS, CASHFLOW_ACCOUNTS
from .statement import FinancialStatement

logger = logging.getLogger(__name__)


class FinancialExtractor:
    """
    Extract financial data from OHADA-compliant Excel financial statements.
    
    Supports:
    - Balance sheets (Bilan Paysage) with Gross/Amortization/Net tracking
    - Income statements (Compte de Résultat)
    - Cash flow statements (Tableau des Flux de Trésorerie)
    - Multi-year consolidation
    - JSON export
    """

    def __init__(self):
        self.workbook = None
        self.raw_data = {}

    def extract_from_excel(self, file_path: Union[str, Path]) -> 'FinancialStatement':
        """
        Extract financial data from a single OHADA Excel file.
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            FinancialStatement object with extracted data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If required sheets are missing
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        self.workbook = openpyxl.load_workbook(file_path, data_only=True)
        self._validate_sheets()
        self._extract_all_statements()
        
        # Extract periods from headers
        periods = self._extract_periods()
        
        from .statement import FinancialStatement
        return FinancialStatement(
            asset_data=self.raw_data.get('assets'),
            liability_data=self.raw_data.get('liabilities'),
            income_data=self.raw_data.get('income'),
            cashflow_data=self.raw_data.get('cashflow'),
            periods=periods,
            file_path=str(file_path),
        )

    def extract_over_period(self, file_list: List[Union[str, Path]]) -> 'FinancialStatement':
        """
        Extract and consolidate financial data from multiple files across years.
        
        Args:
            file_list: List of Excel file paths
            
        Returns:
            Consolidated FinancialStatement
        """
        if len(file_list) < 2:
            raise ValueError("Minimum 2 files required for period analysis")

        combined_asset, combined_liabilities, combined_income, combined_cashflow = (None,) * 4

        statements = []

        # Extract each file individually
        for file_path in file_list:
            statements.append(self.extract_from_excel(file_path))

        # Initialize combined arrays using the first statement
        first = statements[0]
        combined_asset = np.hstack((first.asset_data.copy()[:, [0, -1]], first.asset_data.copy()[:, 1:-1]))
        combined_liabilities = np.hstack((first.liability_data.copy()[:, [0, -1]], first.liability_data.copy()[:, 1:-1]))
        combined_income = np.hstack((first.income_data.copy()[:, [0, -1]], first.income_data.copy()[:, 1:-1]))
        combined_cashflow = np.hstack((first.cashflow_data.copy()[:, [0, -1]], first.cashflow_data.copy()[:, 1:-1]))

        # Merge subsequent years
        for stmt in statements[1:]:
            combined_asset = self._merge_period_data(
                combined_asset, stmt.asset_data,
                combined_col=combined_asset.shape[1] - 1,
                new_col=4,
                label="asset"
            )

            combined_liabilities = self._merge_period_data(
                combined_liabilities, stmt.liability_data,
                combined_col=combined_liabilities.shape[1] - 1,
                new_col=2,
                label="liabilities"
            )

            combined_income = self._merge_period_data(
                combined_income, stmt.income_data,
                combined_col=combined_income.shape[1] - 1,
                new_col=2,
                label="income"
            )

            combined_cashflow = self._merge_period_data(
                combined_cashflow, stmt.cashflow_data,
                combined_col=combined_cashflow.shape[1] - 1,
                new_col=2,
                label="cashflow"
            )

        # Build periods list (sorted by year)
        periods = [stmt.periods[0] for stmt in statements]

        # Replace None value with 0
        for tmp_data in [combined_asset, combined_liabilities, combined_income, combined_cashflow]:
            tmp_data[np.where(tmp_data == None)] = 0

        # Return a proper FinancialStatement
        return FinancialStatement(
            asset_data=combined_asset,
            liability_data=combined_liabilities,
            income_data=combined_income,
            cashflow_data=combined_cashflow,
            periods=periods,
            file_path=";".join(str(p) for p in file_list)
        )

    def _validate_sheets(self):
        """Check that required sheets exist in workbook."""
        workbook_sheets = {' '.join(s.split()).lower() for s in self.workbook.sheetnames}
        required_sheets = {
            stmt.sheet_name.lower() 
            for stmt in OHADA_STATEMENTS.values()
        }
        missing = required_sheets - workbook_sheets
        if missing:
            raise ValueError(f"Missing required sheets: {missing}")
        logger.info(f"Workbook validated: all required sheets present")

    def _extract_all_statements(self):
        """Extract data from all financial statement sheets."""
        for key, stmt_config in OHADA_STATEMENTS.items():
            sheet = self._get_sheet(stmt_config.sheet_name)
            if sheet:
                data = self._extract_sheet_data(
                    sheet, 
                    stmt_config.start_account,
                    stmt_config.end_account,
                    stmt_config.account_count,
                    stmt_config.columns_idx
                )
                
                self.raw_data[key.split('_')[0]] = data

    def _get_sheet(self, sheet_name: str) -> Optional[Worksheet]:
        """Get worksheet by normalized name."""
        for ws in self.workbook.worksheets:
            if ' '.join(ws.title.split()).lower() == sheet_name.lower():
                return ws
        return None

    def _extract_sheet_data(
        self,
        sheet: Worksheet,
        start_code: str, 
        end_code: str, 
        length: int,
        columns: tuple[int, ...]
    ) -> np.ndarray:
        """
        Extract financial data from sheet between start and end codes.
        
        Args:
            sheet: Worksheet to extract from
            start_code: Starting account code (e.g., 'AD')
            end_code: Ending account code (e.g., 'BZ')
            length: Expected number of rows
            
        Returns:
            NumPy array with extracted data
        """
        raw_data = []
        start = False
        liability_column_idx = 7

        for row in sheet.iter_rows(values_only=True):
            if row[0] is None and end_code not in [str(val).upper() for val in row[1:]]:
                continue
                
            # Check if we've found the start code
            if start_code.upper() in str(row).strip().upper():
                if start_code == 'CA' and row[liability_column_idx] is not None:
                    if row[liability_column_idx].strip().upper() == start_code.upper() :
                        start = True
                    elif start:
                        pass
                    else:
                        continue
                    raw_data.append(row[liability_column_idx:])
                else:
                    if row[0].strip().upper() == start_code.upper() :
                        start = True
                    elif start:
                        pass
                    else:
                        continue
                    raw_data.append(row)
            # Check if we've found the end code
            elif str(end_code).upper() in [str(val).strip().upper() for val in row]:
                if start_code == 'CA':
                    if start and str(end_code).upper() == str(row[liability_column_idx]).strip().upper():
                        raw_data.append(row[liability_column_idx:])
                        break
                else:
                    if start and (str(end_code).upper() == str(row[0]).strip().upper() or \
                            str(end_code).upper() == str(row[1:]).strip().upper()):
                        raw_data.append(row)
                        break
            # Extract data between start and end
            elif start:
                if start_code == 'CA':
                    if row[liability_column_idx] is None:
                        continue
                    else:
                        raw_data.append(row[liability_column_idx:])
                else:
                    raw_data.append(row)

        if len(raw_data) == length:
            if columns is None:
                return np.array(raw_data)
            else:
                return np.array(raw_data)[:, columns]
        else:
            logger.warning(
                f"Expected {length} rows, got {len(raw_data)} "
                f"for range {start_code}-{end_code}"
            )
            return np.array(raw_data)

    def _extract_periods(self) -> List[str]:
        """Extract period dates from first available sheet."""
        for ws in self.workbook.worksheets:
            if ws.title.strip().lower() == "fiche r1":
                # Look for dates in header row (usually row 13 Fiche R1)
                cell = ws.cell(row=13, column=6)
                # Check if the cell has a value
                if cell.value:
                    # If the value is a date, format it and return
                    if isinstance(cell.value, datetime):
                        return [cell.value.strftime('%Y-%m-%d'),
                                (cell.value - relativedelta(years=1)).strftime('%Y-%m-%d')]  # Return as a string in YYYY-MM-DD format

                    # If the value is a string and can be converted to a date
                    try:
                        parsed_date = datetime.strptime(cell.value, '%Y-%m-%d')  # Adjust format if needed
                        return [
                            str(cell.value),  # Current string value
                            (parsed_date - relativedelta(years=1)).strftime('%Y-%m-%d')  # Date one year before
                        ]
                    except ValueError:
                        # Handle case where string can't be parsed as date
                        continue
        # Calculate the last day of the previous year
        last_day_last_year = datetime(datetime.now().year - 1, 12, 31)
        return [last_day_last_year.strftime('%Y-%m-%d'),
                (last_day_last_year - relativedelta(years=1)).strftime('%Y-%m-%d') ]  # Return formatted last day of last year

    @staticmethod
    def _check_data_coherence(finStatY: np.ndarray, finStatLY: np.ndarray, i: int, j: int) -> bool:
        """
        Checks whether the financial data for a given column is consistent between the current year and the previous year.

        Args:
            finStatY (np.ndarray): Financial statements for the current year.
            finStatLY (np.ndarray): Financial statements for the previous year.
            i (int): Column index in `finStatY` to validate.
            j (int): Column index in `finStatLY` to validate.

        Returns:
            bool: True if the values in column `i` of the current year are identical
            to the values in column `j` of the previous year.
            False otherwise.
        """
        finStatY[finStatY[:, i] == None, i] = 0
        finStatLY[finStatLY[:, j] == None, j] = 0

        if np.array_equal(finStatY[:, i], finStatLY[:, j]):
            return True
        else:
            return False

    @staticmethod
    def _merge_period_data(
        combined: np.ndarray,
        new_data: np.ndarray,
        combined_col: int,
        new_col: int,
        label: str
    ) -> np.ndarray:
        """
        Merge multi-year financial data with coherence checking.

        Args:
            combined: Existing consolidated data
            new_data: Newly extracted data for the next year
            combined_col: Column index in `combined` to compare
            new_col: Column index in `new_data` to compare
            label: Name of the statement (for logging)

        Returns:
            Updated combined array (or unchanged if incoherent)
        """
        if FinancialExtractor._check_data_coherence(combined, new_data, combined_col, new_col):
            return np.hstack((combined, new_data[:, 1:-1]))
        else:
            logger.warning(f"Incoherence found in {label} data between years.")
            return combined
