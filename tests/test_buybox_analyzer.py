# Tests for BuyBoxAnalyzer class
# Validates analysis logic, offer parsing, and reason determination

from datetime import datetime
from unittest.mock import Mock

from scripts.buybox_analyzer import BuyBoxResult, OfferData


class TestBuyBoxAnalyzerInitialization:
    """Test BuyBoxAnalyzer initialization."""

    def test_analyzer_initialization(self, analyzer_instance):
        """Test that analyzer initializes correctly."""
        assert analyzer_instance is not None
        assert hasattr(analyzer_instance, 'logger')
        assert hasattr(analyzer_instance, 'api')
        assert hasattr(analyzer_instance, 'file')
        assert analyzer_instance.raw_data == []
        assert analyzer_instance.results == []

    def test_analyzer_has_etl_methods(self, analyzer_instance):
        """Test that analyzer has required ETL methods."""
        assert hasattr(analyzer_instance, 'extract')
        assert hasattr(analyzer_instance, 'transform')
        assert hasattr(analyzer_instance, 'load')
        assert hasattr(analyzer_instance, 'main')
        assert callable(analyzer_instance.extract)
        assert callable(analyzer_instance.transform)
        assert callable(analyzer_instance.load)
        assert callable(analyzer_instance.main)


class TestOfferDataClass:
    """Test OfferData dataclass."""

    def test_offer_data_creation(self):
        """Test OfferData can be created with all fields."""
        offer = OfferData(
            seller_id="TEST001",
            listing_price=29.99,
            shipping_cost=5.99,
            is_buy_box_winner=True,
            is_fba=True,
            is_prime=True,
            seller_rating=98.5,
            feedback_count=10000,
            availability="NOW",
            max_shipping_hours=24
        )

        assert offer.seller_id == "TEST001"
        assert offer.listing_price == 29.99
        assert offer.shipping_cost == 5.99
        assert offer.is_buy_box_winner is True
        assert offer.is_fba is True
        assert offer.is_prime is True
        assert offer.seller_rating == 98.5
        assert offer.feedback_count == 10000
        assert offer.availability == "NOW"
        assert offer.max_shipping_hours == 24

    def test_offer_total_price(self):
        """Test total_price property calculation."""
        offer = OfferData(
            seller_id="TEST001",
            listing_price=29.99,
            shipping_cost=5.99,
            is_buy_box_winner=False,
            is_fba=False,
            is_prime=False,
            seller_rating=90.0,
            feedback_count=100,
            availability="NOW",
            max_shipping_hours=48
        )

        assert offer.total_price == 35.98  # 29.99 + 5.99


class TestBuyBoxResultClass:
    """Test BuyBoxResult dataclass."""

    def test_buybox_result_creation(self):
        """Test BuyBoxResult can be created with all fields."""
        result = BuyBoxResult(
            asin="B08N5WRWNW",
            product_name="Test Product",
            winner_seller_id="SELLER001",
            winner_price=29.99,
            winner_shipping=0.0,
            winner_total_price=29.99,
            winner_is_fba=True,
            winner_is_prime=True,
            winner_seller_rating=98.0,
            reasons=["Lowest price", "Prime eligible"],
            total_offers=3,
            analysis_timestamp=datetime.now(),
            error=None
        )

        assert result.asin == "B08N5WRWNW"
        assert result.product_name == "Test Product"
        assert result.winner_seller_id == "SELLER001"
        assert result.error is None

    def test_buybox_result_with_error(self):
        """Test BuyBoxResult with error."""
        result = BuyBoxResult(
            asin="INVALID123",
            product_name="Unknown",
            winner_seller_id=None,
            winner_price=None,
            winner_shipping=None,
            winner_total_price=None,
            winner_is_fba=None,
            winner_is_prime=None,
            winner_seller_rating=None,
            reasons=[],
            total_offers=0,
            analysis_timestamp=datetime.now(),
            error="ASIN not found"
        )

        assert result.winner_seller_id is None
        assert result.error == "ASIN not found"


class TestAnalyzeOffers:
    """Test offer analysis logic."""

    def test_analyze_offers_finds_winner(self, analyzer_instance, sample_offers):
        """Test that analysis correctly identifies Buy Box winner."""
        result = analyzer_instance._analyze_offers(
            sample_offers,
            "B08N5WRWNW",
            "Test Product"
        )

        assert result.winner_seller_id == "SELLER001"
        assert result.winner_is_fba is True
        assert result.winner_is_prime is True
        assert result.total_offers == 3

    def test_analyze_offers_no_winner(self, analyzer_instance):
        """Test analysis when no Buy Box winner exists."""
        offers = [
            OfferData(
                seller_id="SELLER001",
                listing_price=29.99,
                shipping_cost=0.0,
                is_buy_box_winner=False,  # No winner
                is_fba=True,
                is_prime=True,
                seller_rating=98.0,
                feedback_count=15000,
                availability="NOW",
                max_shipping_hours=24
            )
        ]

        result = analyzer_instance._analyze_offers(
            offers,
            "B08N5WRWNW",
            "Test Product"
        )

        assert result.winner_seller_id is None
        assert "No Buy Box winner found" in result.reasons

    def test_analyze_empty_offers(self, analyzer_instance):
        """Test analysis with empty offers list."""
        result = analyzer_instance._analyze_offers(
            [],
            "B08N5WRWNW",
            "Test Product"
        )

        assert result.winner_seller_id is None
        assert result.total_offers == 0


class TestDetermineReasons:
    """Test reason determination logic."""

    def test_lowest_price_reason(self, analyzer_instance, sample_offers):
        """Test that lowest price is identified as a reason."""
        winner = sample_offers[0]  # SELLER001 with $29.99 total

        reasons = analyzer_instance._determine_reasons(winner, sample_offers)

        assert any("Lowest total price" in r for r in reasons)

    def test_fba_reason(self, analyzer_instance, sample_offers):
        """Test that FBA is identified as a reason."""
        winner = sample_offers[0]  # FBA seller

        reasons = analyzer_instance._determine_reasons(winner, sample_offers)

        assert any("Fulfilled by Amazon" in r for r in reasons)

    def test_prime_reason(self, analyzer_instance, sample_offers):
        """Test that Prime eligibility is identified as a reason."""
        winner = sample_offers[0]  # Prime eligible

        reasons = analyzer_instance._determine_reasons(winner, sample_offers)

        assert any("Prime eligible" in r for r in reasons)

    def test_excellent_rating_reason(self, analyzer_instance, sample_offers):
        """Test that excellent seller rating is identified."""
        winner = sample_offers[0]  # 98% rating

        reasons = analyzer_instance._determine_reasons(winner, sample_offers)

        assert any("Excellent seller rating" in r for r in reasons)

    def test_high_feedback_reason(self, analyzer_instance, sample_offers):
        """Test that high feedback volume is identified."""
        winner = sample_offers[0]  # 15000 feedback count

        reasons = analyzer_instance._determine_reasons(winner, sample_offers)

        assert any("feedback volume" in r.lower() for r in reasons)

    def test_fast_shipping_reason(self, analyzer_instance, sample_offers):
        """Test that fast shipping is identified."""
        winner = sample_offers[0]  # 24h max shipping

        reasons = analyzer_instance._determine_reasons(winner, sample_offers)

        assert any("Fast shipping" in r for r in reasons)


class TestParseOffers:
    """Test offer parsing from API response."""

    def test_parse_offers_valid_data(self, analyzer_instance):
        """Test parsing valid offer data."""
        raw_offers = [
            {
                "seller_id": "SELLER001",
                "listing_price": 29.99,
                "shipping_cost": 0.0,
                "is_buy_box_winner": True,
                "is_fba": True,
                "is_prime": True,
                "seller_rating": 98.0,
                "feedback_count": 15000,
                "availability": "NOW",
                "max_shipping_hours": 24
            }
        ]

        offers = analyzer_instance._parse_offers(raw_offers)

        assert len(offers) == 1
        assert offers[0].seller_id == "SELLER001"
        assert offers[0].is_buy_box_winner is True

    def test_parse_offers_empty_list(self, analyzer_instance):
        """Test parsing empty offers list."""
        offers = analyzer_instance._parse_offers([])
        assert offers == []

    def test_parse_offers_with_missing_fields(self, analyzer_instance):
        """Test parsing offers with missing optional fields."""
        raw_offers = [
            {
                "seller_id": "SELLER001",
                "listing_price": 29.99
                # Missing other fields
            }
        ]

        offers = analyzer_instance._parse_offers(raw_offers)

        # Should handle missing fields gracefully
        assert len(offers) == 1
        assert offers[0].shipping_cost == 0.0  # Default value


class TestProgressCallback:
    """Test progress callback functionality."""

    def test_set_progress_callback(self, analyzer_instance):
        """Test setting progress callback."""
        callback = Mock()
        analyzer_instance.set_progress_callback(callback)

        assert analyzer_instance.progress_callback == callback

    def test_update_progress_calls_callback(self, analyzer_instance):
        """Test that _update_progress calls the callback."""
        callback = Mock()
        analyzer_instance.set_progress_callback(callback)

        analyzer_instance._update_progress(1, 10, "Processing")

        callback.assert_called_once_with(1, 10, "Processing")

    def test_update_progress_no_callback(self, analyzer_instance):
        """Test that _update_progress handles no callback gracefully."""
        # Should not raise an error
        analyzer_instance._update_progress(1, 10, "Processing")
