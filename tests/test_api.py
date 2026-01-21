# Tests for API utility class
# Validates SP-API client, rate limiting, and response parsing

import time
from unittest.mock import Mock, patch

import pytest

from utils.api import API, RateLimiter


class TestRateLimiter:
    """Test RateLimiter class."""

    def test_rate_limiter_initialization(self):
        """Test rate limiter initializes correctly."""
        limiter = RateLimiter(requests_per_second=1.0, burst=2)

        assert limiter.min_interval == 1.0
        assert limiter.burst == 2
        assert limiter.tokens == 2.0

    def test_rate_limiter_acquire(self):
        """Test rate limiter allows initial burst."""
        limiter = RateLimiter(requests_per_second=10.0, burst=3)

        # Should allow 3 quick requests (burst)
        start = time.time()
        limiter.acquire()
        limiter.acquire()
        limiter.acquire()
        elapsed = time.time() - start

        # Should be nearly instant for burst
        assert elapsed < 0.5

    def test_rate_limiter_throttles(self):
        """Test rate limiter throttles after burst."""
        limiter = RateLimiter(requests_per_second=10.0, burst=1)

        # First request should be instant
        limiter.acquire()

        # Second request should be delayed
        start = time.time()
        limiter.acquire()
        elapsed = time.time() - start

        # Should have waited approximately 0.1 seconds (1/10 req/sec)
        assert elapsed >= 0.05


class TestAPIInitialization:
    """Test API class initialization."""

    def test_api_initialization(self, api_instance):
        """Test API initializes correctly."""
        assert api_instance is not None
        assert hasattr(api_instance, 'logger')
        assert hasattr(api_instance, 'credentials')
        assert hasattr(api_instance, '_pricing_limiter')
        assert hasattr(api_instance, '_catalog_limiter')

    def test_api_marketplace_constant(self):
        """Test US marketplace constant is set correctly."""
        assert API.MARKETPLACE_US == "ATVPDKIKX0DER"


class TestAPIConfiguration:
    """Test API configuration methods."""

    def test_configure_credentials(self, api_instance):
        """Test configuring API credentials."""
        api_instance.configure(
            refresh_token="test_refresh_token",
            client_id="test_client_id",
            client_secret="test_client_secret"
        )

        assert api_instance.credentials is not None
        assert api_instance.credentials["refresh_token"] == "test_refresh_token"
        assert api_instance.credentials["lwa_app_id"] == "test_client_id"
        assert api_instance.credentials["lwa_client_secret"] == "test_client_secret"

    def test_configure_resets_api_clients(self, api_instance):
        """Test that configuring credentials resets API clients."""
        # Set up mock clients
        api_instance._products_api = Mock()
        api_instance._catalog_api = Mock()

        api_instance.configure(
            refresh_token="new_token",
            client_id="new_id",
            client_secret="new_secret"
        )

        # Should reset clients
        assert api_instance._products_api is None
        assert api_instance._catalog_api is None


class TestAPICredentialValidation:
    """Test credential validation."""

    def test_get_products_api_without_credentials(self, api_instance):
        """Test that getting Products API without credentials raises error."""
        api_instance.credentials = None

        with pytest.raises(ValueError, match="credentials not configured"):
            api_instance._get_products_api()

    def test_get_catalog_api_without_credentials(self, api_instance):
        """Test that getting Catalog API without credentials raises error."""
        api_instance.credentials = None

        with pytest.raises(ValueError, match="credentials not configured"):
            api_instance._get_catalog_api()


class TestParseOffersResponse:
    """Test offer response parsing."""

    def test_parse_offers_response_valid(self, api_instance):
        """Test parsing valid offers response."""
        payload = {
            "Offers": [
                {
                    "SellerId": "SELLER001",
                    "ListingPrice": {"CurrencyCode": "USD", "Amount": 29.99},
                    "Shipping": {"CurrencyCode": "USD", "Amount": 0.0},
                    "IsBuyBoxWinner": True,
                    "IsFulfilledByAmazon": True,
                    "PrimeInformation": {"IsPrime": True},
                    "SellerFeedbackRating": {
                        "FeedbackCount": 15000,
                        "SellerPositiveFeedbackRating": 98
                    },
                    "ShippingTime": {
                        "maximumHours": 24,
                        "availabilityType": "NOW"
                    }
                }
            ]
        }

        offers = api_instance._parse_offers_response(payload)

        assert len(offers) == 1
        assert offers[0]["seller_id"] == "SELLER001"
        assert offers[0]["listing_price"] == 29.99
        assert offers[0]["shipping_cost"] == 0.0
        assert offers[0]["is_buy_box_winner"] is True
        assert offers[0]["is_fba"] is True
        assert offers[0]["is_prime"] is True
        assert offers[0]["seller_rating"] == 98
        assert offers[0]["feedback_count"] == 15000
        assert offers[0]["availability"] == "NOW"
        assert offers[0]["max_shipping_hours"] == 24

    def test_parse_offers_response_empty(self, api_instance):
        """Test parsing empty offers response."""
        payload = {"Offers": []}

        offers = api_instance._parse_offers_response(payload)

        assert offers == []

    def test_parse_offers_response_missing_fields(self, api_instance):
        """Test parsing offers with missing fields."""
        payload = {
            "Offers": [
                {
                    "SellerId": "SELLER001"
                    # Missing most fields
                }
            ]
        }

        offers = api_instance._parse_offers_response(payload)

        assert len(offers) == 1
        assert offers[0]["seller_id"] == "SELLER001"
        assert offers[0]["listing_price"] == 0.0  # Default
        assert offers[0]["is_buy_box_winner"] is False  # Default


class TestTestConnection:
    """Test connection testing."""

    def test_test_connection_no_credentials(self, api_instance):
        """Test connection test fails without credentials."""
        api_instance.credentials = None

        result = api_instance.test_connection()

        assert result is False

    @patch.object(API, '_get_catalog_api')
    def test_test_connection_success(self, mock_get_catalog, api_instance):
        """Test successful connection test."""
        api_instance.credentials = {
            "refresh_token": "test",
            "lwa_app_id": "test",
            "lwa_client_secret": "test"
        }

        mock_catalog = Mock()
        mock_catalog.get_catalog_item.return_value = Mock(payload={})
        mock_get_catalog.return_value = mock_catalog

        result = api_instance.test_connection()

        assert result is True


class TestGetItemOffersBatch:
    """Test batch offer fetching."""

    @patch.object(API, 'get_item_offers')
    @patch.object(API, 'get_product_name')
    def test_get_item_offers_batch(self, mock_get_name, mock_get_offers, api_instance):
        """Test batch fetching for multiple ASINs."""
        mock_get_offers.return_value = [{"seller_id": "TEST"}]
        mock_get_name.return_value = "Test Product"

        results = api_instance.get_item_offers_batch(["ASIN1", "ASIN2"])

        assert len(results) == 2
        assert results[0]["asin"] == "ASIN1"
        assert results[0]["product_name"] == "Test Product"
        assert results[0]["error"] is None

    @patch.object(API, 'get_item_offers')
    @patch.object(API, 'get_product_name')
    def test_get_item_offers_batch_with_error(self, mock_get_name, mock_get_offers, api_instance):
        """Test batch fetching handles errors gracefully."""
        mock_get_offers.side_effect = Exception("API Error")
        mock_get_name.return_value = "Test Product"

        results = api_instance.get_item_offers_batch(["ASIN1"])

        assert len(results) == 1
        assert results[0]["asin"] == "ASIN1"
        assert results[0]["error"] is not None
        assert "API Error" in results[0]["error"]
