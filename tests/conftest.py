# Pytest configuration and fixtures
# Provides common test utilities and setup for all tests

import logging
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from scripts.buybox_analyzer import BuyBoxAnalyzer, BuyBoxResult, OfferData
from utils.api import API
from utils.file import File


@pytest.fixture
def sample_dataframe():
    """
    Create a sample DataFrame for testing.

    Returns
    -------
    pd.DataFrame
        Sample DataFrame with test data.
    """
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'amount': [100.50, 250.75, 150.25, 300.00, 75.80],
        'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05']),
        'status': ['active', 'inactive', 'active', 'pending', 'active']
    })


@pytest.fixture
def empty_dataframe():
    """
    Create an empty DataFrame for testing edge cases.

    Returns
    -------
    pd.DataFrame
        Empty DataFrame.
    """
    return pd.DataFrame()


@pytest.fixture
def test_logger():
    """
    Create a test logger for testing.

    Returns
    -------
    logging.Logger
        Configured test logger.
    """
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Add console handler for test output
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


@pytest.fixture
def temp_directory():
    """
    Create a temporary directory for test files.

    Yields
    ------
    Path
        Path to temporary directory.
    """
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir

    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def analyzer_instance():
    """
    Create a BuyBoxAnalyzer instance for testing.

    Yields
    ------
    BuyBoxAnalyzer
        BuyBoxAnalyzer instance.
    """
    analyzer = BuyBoxAnalyzer('test/test_analyzer.log')
    yield analyzer
    analyzer.dispose()


@pytest.fixture
def api_instance():
    """
    Create an API utility instance for testing.

    Yields
    ------
    API
        API utility instance.
    """
    api = API(instance_id=1)
    yield api


@pytest.fixture
def file_instance(temp_directory, monkeypatch):
    """
    Create a File utility instance for testing.

    Parameters
    ----------
    temp_directory : Path
        Temporary directory fixture.
    monkeypatch : pytest.MonkeyPatch
        Pytest monkeypatch fixture.

    Yields
    ------
    File
        File utility instance.
    """
    # Set environment variables to use temp directory
    monkeypatch.setenv("OUTPUT_PATH", str(temp_directory / "output"))

    file = File(instance_id=1)
    yield file


@pytest.fixture
def sample_offers():
    """
    Create sample offer data for testing.

    Returns
    -------
    List[OfferData]
        List of sample offers.
    """
    return [
        OfferData(
            seller_id="SELLER001",
            listing_price=29.99,
            shipping_cost=0.0,
            is_buy_box_winner=True,
            is_fba=True,
            is_prime=True,
            seller_rating=98.0,
            feedback_count=15000,
            availability="NOW",
            max_shipping_hours=24
        ),
        OfferData(
            seller_id="SELLER002",
            listing_price=28.50,
            shipping_cost=4.99,
            is_buy_box_winner=False,
            is_fba=False,
            is_prime=False,
            seller_rating=92.0,
            feedback_count=500,
            availability="NOW",
            max_shipping_hours=72
        ),
        OfferData(
            seller_id="SELLER003",
            listing_price=31.00,
            shipping_cost=0.0,
            is_buy_box_winner=False,
            is_fba=True,
            is_prime=True,
            seller_rating=95.0,
            feedback_count=8000,
            availability="NOW",
            max_shipping_hours=48
        )
    ]


@pytest.fixture
def sample_buybox_results():
    """
    Create sample Buy Box results for testing.

    Returns
    -------
    List[BuyBoxResult]
        List of sample results.
    """
    return [
        BuyBoxResult(
            asin="B08N5WRWNW",
            product_name="Test Product 1",
            winner_seller_id="SELLER001",
            winner_price=29.99,
            winner_shipping=0.0,
            winner_total_price=29.99,
            winner_is_fba=True,
            winner_is_prime=True,
            winner_seller_rating=98.0,
            reasons=["Lowest total price ($29.99)", "Fulfilled by Amazon (FBA)", "Prime eligible"],
            total_offers=3,
            analysis_timestamp=datetime.now(),
            error=None
        ),
        BuyBoxResult(
            asin="B07XJ8C8F5",
            product_name="Test Product 2",
            winner_seller_id=None,
            winner_price=None,
            winner_shipping=None,
            winner_total_price=None,
            winner_is_fba=None,
            winner_is_prime=None,
            winner_seller_rating=None,
            reasons=["No Buy Box winner found"],
            total_offers=0,
            analysis_timestamp=datetime.now(),
            error="ASIN not found"
        )
    ]


@pytest.fixture
def sample_csv_file(temp_directory, sample_dataframe):
    """
    Create a sample CSV file for testing.

    Parameters
    ----------
    temp_directory : Path
        Temporary directory fixture.
    sample_dataframe : pd.DataFrame
        Sample DataFrame fixture.

    Returns
    -------
    Path
        Path to sample CSV file.
    """
    csv_file = temp_directory / "sample.csv"
    sample_dataframe.to_csv(csv_file, index=False)
    return csv_file


@pytest.fixture
def sample_excel_file(temp_directory, sample_dataframe):
    """
    Create a sample Excel file for testing.

    Parameters
    ----------
    temp_directory : Path
        Temporary directory fixture.
    sample_dataframe : pd.DataFrame
        Sample DataFrame fixture.

    Returns
    -------
    Path
        Path to sample Excel file.
    """
    excel_file = temp_directory / "sample.xlsx"
    sample_dataframe.to_excel(excel_file, index=False)
    return excel_file


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """
    Set up test environment variables.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Pytest monkeypatch fixture.
    """
    # Set test environment variables
    test_env_vars = {
        "ENVIRONMENT": "test",
        "DEBUG_MODE": "true",
        "LOG_LEVEL": "DEBUG",
        "SP_API_MARKETPLACE_ID": "ATVPDKIKX0DER"
    }

    for key, value in test_env_vars.items():
        monkeypatch.setenv(key, value)


# Sample API response for mocking
SAMPLE_OFFERS_RESPONSE = {
    "Offers": [
        {
            "SellerId": "SELLER001",
            "ListingPrice": {"CurrencyCode": "USD", "Amount": 29.99},
            "Shipping": {"CurrencyCode": "USD", "Amount": 0.0},
            "IsBuyBoxWinner": True,
            "IsFulfilledByAmazon": True,
            "PrimeInformation": {"IsPrime": True, "IsNationalPrime": True},
            "SellerFeedbackRating": {
                "FeedbackCount": 15000,
                "SellerPositiveFeedbackRating": 98
            },
            "ShippingTime": {
                "maximumHours": 24,
                "minimumHours": 12,
                "availabilityType": "NOW"
            }
        },
        {
            "SellerId": "SELLER002",
            "ListingPrice": {"CurrencyCode": "USD", "Amount": 28.50},
            "Shipping": {"CurrencyCode": "USD", "Amount": 4.99},
            "IsBuyBoxWinner": False,
            "IsFulfilledByAmazon": False,
            "PrimeInformation": {"IsPrime": False},
            "SellerFeedbackRating": {
                "FeedbackCount": 500,
                "SellerPositiveFeedbackRating": 92
            },
            "ShippingTime": {
                "maximumHours": 72,
                "minimumHours": 48,
                "availabilityType": "NOW"
            }
        }
    ]
}

SAMPLE_CATALOG_RESPONSE = {
    "asin": "B08N5WRWNW",
    "summaries": [
        {
            "marketplaceId": "ATVPDKIKX0DER",
            "itemName": "Test Product - Sample Item for Testing",
            "brandName": "TestBrand"
        }
    ]
}
