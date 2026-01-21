# File utility class for Excel export and file operations
# Handles Buy Box analysis output and environment file management
# Note: xlsxwriter lacks type stubs, so we use type: ignore for its methods

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd


class File:
    """
    File utility for Excel export and environment file management.

    Provides methods to write Buy Box analysis results to formatted Excel
    and manage .env file for credential storage.
    """

    def __init__(self, instance_id: Optional[int] = None):
        """
        Initialize the File utility.

        Parameters
        ----------
        instance_id : int, optional
            Instance ID for logging purposes
        """
        if instance_id:
            logger_name = f"utils.file.instance_{instance_id}"
        else:
            logger_name = "utils.file"
        self.logger = logging.getLogger(logger_name)
        self.logger.info("Initialized File utility")

    # MARK: Excel Operations
    def write_buybox_excel(self, results: List[Any], output_path: str) -> str:
        """
        Write Buy Box analysis results to formatted Excel file.

        Parameters
        ----------
        results : List[BuyBoxResult]
            List of Buy Box analysis results
        output_path : str
            Path for output Excel file

        Returns
        -------
        str
            Path to the created Excel file
        """
        try:
            # Create output directory if needed
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Convert results to DataFrame
            data = []
            for result in results:
                data.append({
                    "ASIN": result.asin,
                    "Product Name": result.product_name,
                    "Buy Box Winner": result.winner_seller_id or "No Winner",
                    "Price": result.winner_price,
                    "Shipping": result.winner_shipping,
                    "Total Price": result.winner_total_price,
                    "Is FBA": "Yes" if result.winner_is_fba else "No" if result.winner_is_fba is not None else "",
                    "Is Prime": "Yes" if result.winner_is_prime else "No" if result.winner_is_prime is not None else "",
                    "Seller Rating": f"{result.winner_seller_rating:.0f}%" if result.winner_seller_rating else "",
                    "Reasons": "; ".join(result.reasons) if result.reasons else "",
                    "Total Offers": result.total_offers,
                    "Analyzed At": result.analysis_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "Error": result.error or ""
                })

            df = pd.DataFrame(data)

            # Write to Excel with formatting
            with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name="Buy Box Analysis", index=False)

                # Get workbook and worksheet (xlsxwriter types)
                workbook: Any = writer.book
                worksheet: Any = writer.sheets["Buy Box Analysis"]

                # Define formats
                header_format = workbook.add_format({
                    "bold": True,
                    "bg_color": "#FF9900",  # Amazon orange
                    "font_color": "white",
                    "border": 1,
                    "align": "center",
                    "valign": "vcenter"
                })

                currency_format = workbook.add_format({
                    "num_format": "$#,##0.00",
                    "align": "right"
                })

                text_wrap_format = workbook.add_format({
                    "text_wrap": True,
                    "valign": "top"
                })

                error_format = workbook.add_format({
                    "font_color": "red"
                })

                # Apply header format
                for col_num, col_name in enumerate(df.columns):
                    worksheet.write(0, col_num, col_name, header_format)

                # Set column widths
                column_widths = {
                    "ASIN": 15,
                    "Product Name": 50,
                    "Buy Box Winner": 18,
                    "Price": 12,
                    "Shipping": 12,
                    "Total Price": 12,
                    "Is FBA": 10,
                    "Is Prime": 10,
                    "Seller Rating": 14,
                    "Reasons": 60,
                    "Total Offers": 12,
                    "Analyzed At": 20,
                    "Error": 30
                }

                for col_num, col_name in enumerate(df.columns):
                    width = column_widths.get(col_name, 15)
                    worksheet.set_column(col_num, col_num, width)

                # Apply currency format to price columns
                price_cols = ["Price", "Shipping", "Total Price"]
                for col_name in price_cols:
                    if col_name in df.columns:
                        col_idx = df.columns.get_loc(col_name)
                        for row_num in range(1, len(df) + 1):
                            value = df.iloc[row_num - 1][col_name]
                            if pd.notna(value):
                                worksheet.write(row_num, col_idx, value, currency_format)

                # Apply text wrap to Reasons column
                reasons_col = df.columns.get_loc("Reasons")
                worksheet.set_column(reasons_col, reasons_col, 60, text_wrap_format)

                # Apply error format to Error column
                error_col = df.columns.get_loc("Error")
                for row_num in range(1, len(df) + 1):
                    error_value = df.iloc[row_num - 1]["Error"]
                    if error_value:
                        worksheet.write(row_num, error_col, error_value, error_format)

                # Freeze top row
                worksheet.freeze_panes(1, 0)

                # Add autofilter
                worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)

            self.logger.info(f"Excel file saved: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Failed to write Excel file: {e}")
            raise

    # MARK: Environment File Operations
    def update_env_file(self, updates: Dict[str, str], env_path: str = ".env") -> None:
        """
        Update .env file with new values.

        Creates the file if it doesn't exist. Updates existing keys
        or appends new ones.

        Parameters
        ----------
        updates : Dict[str, str]
            Dictionary of key-value pairs to update
        env_path : str, optional
            Path to .env file, defaults to ".env"
        """
        try:
            # Read existing content
            existing = self.read_env_file(env_path)

            # Update with new values
            existing.update(updates)

            # Write back to file
            with open(env_path, "w") as f:
                # Write header
                f.write("# Environment Variables for Amazon Buy Box Analyzer\n")
                f.write("# Auto-generated - DO NOT commit to version control\n\n")

                # Write SP-API section
                f.write("# Amazon SP-API Configuration\n")
                sp_api_keys = ["SP_API_REFRESH_TOKEN", "SP_API_CLIENT_ID",
                               "SP_API_CLIENT_SECRET", "SP_API_MARKETPLACE_ID"]

                for key in sp_api_keys:
                    if key in existing:
                        f.write(f"{key}={existing[key]}\n")

                # Write any other keys
                f.write("\n# Other Settings\n")
                for key, value in existing.items():
                    if key not in sp_api_keys:
                        f.write(f"{key}={value}\n")

            self.logger.info(f"Updated .env file: {env_path}")

        except Exception as e:
            self.logger.error(f"Failed to update .env file: {e}")
            raise

    def read_env_file(self, env_path: str = ".env") -> Dict[str, str]:
        """
        Read current .env file values.

        Parameters
        ----------
        env_path : str, optional
            Path to .env file, defaults to ".env"

        Returns
        -------
        Dict[str, str]
            Dictionary of environment variables
        """
        env_vars: Dict[str, str] = {}

        try:
            if not os.path.exists(env_path):
                return env_vars

            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith("#"):
                        continue

                    # Parse key=value
                    if "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()

            return env_vars

        except Exception as e:
            self.logger.warning(f"Failed to read .env file: {e}")
            return env_vars

    def get_default_output_path(self) -> str:
        """
        Get default output path for Excel file.

        Returns
        -------
        str
            Default output path with timestamp
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.getenv("OUTPUT_PATH", "./output")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        return os.path.join(output_dir, f"buybox_analysis_{timestamp}.xlsx")
