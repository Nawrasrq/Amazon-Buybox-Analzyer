# Tests for File utility class
# Validates Excel export and environment file operations

import os
from datetime import datetime

import pandas as pd

from scripts.buybox_analyzer import BuyBoxResult


class TestFileInitialization:
    """Test File class initialization."""

    def test_file_initialization(self, file_instance):
        """Test File initializes correctly."""
        assert file_instance is not None
        assert hasattr(file_instance, 'logger')


class TestWriteBuyboxExcel:
    """Test Excel export functionality."""

    def test_write_buybox_excel_creates_file(self, file_instance, temp_directory, sample_buybox_results):
        """Test that Excel file is created."""
        output_path = str(temp_directory / "test_output.xlsx")

        result_path = file_instance.write_buybox_excel(sample_buybox_results, output_path)

        assert os.path.exists(result_path)
        assert result_path == output_path

    def test_write_buybox_excel_content(self, file_instance, temp_directory, sample_buybox_results):
        """Test that Excel file contains correct data."""
        output_path = str(temp_directory / "test_output.xlsx")

        file_instance.write_buybox_excel(sample_buybox_results, output_path)

        # Read back the Excel file
        df = pd.read_excel(output_path)

        assert len(df) == 2
        assert "ASIN" in df.columns
        assert "Product Name" in df.columns
        assert "Buy Box Winner" in df.columns
        assert "Reasons" in df.columns

    def test_write_buybox_excel_empty_results(self, file_instance, temp_directory):
        """Test writing empty results list."""
        output_path = str(temp_directory / "empty_output.xlsx")

        file_instance.write_buybox_excel([], output_path)

        assert os.path.exists(output_path)
        df = pd.read_excel(output_path)
        assert len(df) == 0

    def test_write_buybox_excel_creates_directory(self, file_instance, temp_directory):
        """Test that output directory is created if it doesn't exist."""
        output_path = str(temp_directory / "new_dir" / "output.xlsx")

        result = BuyBoxResult(
            asin="B08N5WRWNW",
            product_name="Test",
            winner_seller_id="SELLER",
            winner_price=29.99,
            winner_shipping=0.0,
            winner_total_price=29.99,
            winner_is_fba=True,
            winner_is_prime=True,
            winner_seller_rating=98.0,
            reasons=["Test reason"],
            total_offers=1,
            analysis_timestamp=datetime.now(),
            error=None
        )

        file_instance.write_buybox_excel([result], output_path)

        assert os.path.exists(output_path)


class TestEnvFileOperations:
    """Test .env file operations."""

    def test_read_env_file_not_exists(self, file_instance, temp_directory):
        """Test reading non-existent .env file."""
        env_path = str(temp_directory / ".env.nonexistent")

        result = file_instance.read_env_file(env_path)

        assert result == {}

    def test_read_env_file(self, file_instance, temp_directory):
        """Test reading existing .env file."""
        env_path = str(temp_directory / ".env")

        # Create test .env file
        with open(env_path, "w") as f:
            f.write("KEY1=value1\n")
            f.write("KEY2=value2\n")
            f.write("# Comment line\n")
            f.write("\n")  # Empty line
            f.write("KEY3=value with spaces\n")

        result = file_instance.read_env_file(env_path)

        assert result["KEY1"] == "value1"
        assert result["KEY2"] == "value2"
        assert result["KEY3"] == "value with spaces"
        assert "Comment" not in str(result)

    def test_update_env_file_new_file(self, file_instance, temp_directory):
        """Test creating new .env file."""
        env_path = str(temp_directory / ".env.new")

        file_instance.update_env_file({
            "SP_API_REFRESH_TOKEN": "test_token",
            "SP_API_CLIENT_ID": "test_id"
        }, env_path)

        assert os.path.exists(env_path)

        # Verify content
        result = file_instance.read_env_file(env_path)
        assert result["SP_API_REFRESH_TOKEN"] == "test_token"
        assert result["SP_API_CLIENT_ID"] == "test_id"

    def test_update_env_file_updates_existing(self, file_instance, temp_directory):
        """Test updating existing .env file."""
        env_path = str(temp_directory / ".env")

        # Create initial file
        with open(env_path, "w") as f:
            f.write("SP_API_REFRESH_TOKEN=old_token\n")
            f.write("OTHER_KEY=other_value\n")

        # Update
        file_instance.update_env_file({
            "SP_API_REFRESH_TOKEN": "new_token",
            "SP_API_CLIENT_ID": "new_id"
        }, env_path)

        # Verify updates
        result = file_instance.read_env_file(env_path)
        assert result["SP_API_REFRESH_TOKEN"] == "new_token"
        assert result["SP_API_CLIENT_ID"] == "new_id"
        assert result["OTHER_KEY"] == "other_value"


class TestGetDefaultOutputPath:
    """Test default output path generation."""

    def test_get_default_output_path(self, file_instance, temp_directory, monkeypatch):
        """Test default output path generation."""
        monkeypatch.setenv("OUTPUT_PATH", str(temp_directory / "output"))

        path = file_instance.get_default_output_path()

        assert "buybox_analysis" in path
        assert path.endswith(".xlsx")
        assert os.path.exists(os.path.dirname(path))

    def test_get_default_output_path_creates_directory(self, file_instance, temp_directory, monkeypatch):
        """Test that output directory is created."""
        output_dir = str(temp_directory / "new_output_dir")
        monkeypatch.setenv("OUTPUT_PATH", output_dir)

        _ = file_instance.get_default_output_path()

        assert os.path.exists(output_dir)
