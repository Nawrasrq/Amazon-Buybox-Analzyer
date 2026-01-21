# Amazon SP-API client for Buy Box analysis
# Handles authentication, rate limiting, and API calls to Amazon Selling Partner API

import logging
import os
import threading
import time
from typing import Any, Dict, List, Optional

from sp_api.api import CatalogItems, Products
from sp_api.base import Marketplaces, SellingApiException
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config.marketplaces import DEFAULT_MARKETPLACE


class RateLimiter:
    """
    Token bucket rate limiter for API calls.

    Ensures API calls don't exceed the allowed rate to avoid throttling.
    """

    def __init__(self, requests_per_second: float, burst: int):
        """
        Initialize the rate limiter.

        Parameters
        ----------
        requests_per_second : float
            Maximum sustained request rate
        burst : int
            Maximum burst capacity
        """
        self.min_interval = 1.0 / requests_per_second
        self.burst = burst
        self.tokens = float(burst)
        self.last_request = time.time()
        self._lock = threading.Lock()

    def acquire(self) -> None:
        """
        Wait until a request can be made.

        Blocks if rate limit would be exceeded.
        """
        with self._lock:
            now = time.time()
            elapsed = now - self.last_request

            # Replenish tokens based on elapsed time
            self.tokens = min(self.burst, self.tokens + elapsed / self.min_interval)

            if self.tokens < 1:
                sleep_time = (1 - self.tokens) * self.min_interval
                time.sleep(sleep_time)
                self.tokens = 1.0

            self.tokens -= 1
            self.last_request = time.time()


class API:
    """
    Amazon SP-API client with rate limiting and retry logic.

    Provides methods to fetch product offers and catalog information
    for Buy Box analysis.
    """

    # US Marketplace ID
    MARKETPLACE_US = DEFAULT_MARKETPLACE["id"]

    def __init__(self, instance_id: Optional[int] = None):
        """
        Initialize the API utility.

        Parameters
        ----------
        instance_id : int, optional
            Instance ID for logging purposes
        """
        if instance_id:
            logger_name = f"utils.api.instance_{instance_id}"
        else:
            logger_name = "utils.api"
        self.logger = logging.getLogger(logger_name)

        self.credentials: Optional[Dict[str, str]] = None
        self._products_api: Optional[Products] = None
        self._catalog_api: Optional[CatalogItems] = None

        # Rate limiters for different API endpoints
        # Product Pricing API: 0.5 requests/second, burst 1
        self._pricing_limiter = RateLimiter(0.5, 1)
        # Catalog Items API: 2 requests/second, burst 2
        self._catalog_limiter = RateLimiter(2.0, 2)

        self._load_credentials_from_env()
        self.logger.info("Initialized API utility")

    # MARK: Configuration
    def _load_credentials_from_env(self) -> None:
        """Load SP-API credentials from environment variables."""
        refresh_token = os.getenv("SP_API_REFRESH_TOKEN", "")
        client_id = os.getenv("SP_API_CLIENT_ID", "")
        client_secret = os.getenv("SP_API_CLIENT_SECRET", "")

        if refresh_token and client_id and client_secret:
            self.credentials = {
                "refresh_token": refresh_token,
                "lwa_app_id": client_id,
                "lwa_client_secret": client_secret
            }
            self.logger.info("Loaded SP-API credentials from environment")
        else:
            self.logger.warning("SP-API credentials not found in environment")

    def configure(self, refresh_token: str, client_id: str, client_secret: str) -> None:
        """
        Configure SP-API credentials.

        Parameters
        ----------
        refresh_token : str
            LWA refresh token
        client_id : str
            LWA client ID
        client_secret : str
            LWA client secret
        """
        self.credentials = {
            "refresh_token": refresh_token,
            "lwa_app_id": client_id,
            "lwa_client_secret": client_secret
        }

        # Reset API clients to use new credentials
        self._products_api = None
        self._catalog_api = None

        self.logger.info("SP-API credentials configured")

    def _get_products_api(self) -> Products:
        """
        Get or create Products API client.

        Returns
        -------
        Products
            SP-API Products client

        Raises
        ------
        ValueError
            If credentials are not configured
        """
        if not self.credentials:
            raise ValueError("SP-API credentials not configured")

        if self._products_api is None:
            self._products_api = Products(
                credentials=self.credentials,
                marketplace=Marketplaces.US
            )

        return self._products_api

    def _get_catalog_api(self) -> CatalogItems:
        """
        Get or create Catalog Items API client.

        Returns
        -------
        CatalogItems
            SP-API Catalog Items client

        Raises
        ------
        ValueError
            If credentials are not configured
        """
        if not self.credentials:
            raise ValueError("SP-API credentials not configured")

        if self._catalog_api is None:
            self._catalog_api = CatalogItems(
                credentials=self.credentials,
                marketplace=Marketplaces.US
            )

        return self._catalog_api

    def test_connection(self) -> bool:
        """
        Test SP-API connection with a sample request.

        Returns
        -------
        bool
            True if connection successful, False otherwise
        """
        try:
            if not self.credentials:
                self.logger.error("No credentials configured")
                return False

            # Try to get catalog info for a well-known ASIN
            test_asin = "B08N5WRWNW"  # Common test ASIN
            self._catalog_limiter.acquire()

            catalog_api = self._get_catalog_api()
            _ = catalog_api.get_catalog_item(
                asin=test_asin,
                marketplaceIds=[self.MARKETPLACE_US],
                includedData=["summaries"]
            )

            self.logger.info("SP-API connection test successful")
            return True

        except SellingApiException as e:
            self.logger.error(f"SP-API connection test failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Connection test error: {e}")
            return False

    # MARK: API Methods
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((SellingApiException,))
    )
    def get_item_offers(self, asin: str) -> List[Dict[str, Any]]:
        """
        Get all offers for an ASIN.

        Parameters
        ----------
        asin : str
            Amazon Standard Identification Number

        Returns
        -------
        List[Dict[str, Any]]
            List of parsed offer data dictionaries
        """
        self._pricing_limiter.acquire()

        try:
            products_api = self._get_products_api()
            response = products_api.get_item_offers(
                asin=asin,
                item_condition="New"
            )

            return self._parse_offers_response(response.payload)

        except SellingApiException as e:
            if e.code == 404:
                self.logger.warning(f"ASIN not found: {asin}")
                return []
            self.logger.error(f"Failed to get offers for {asin}: {e}")
            raise

    def _parse_offers_response(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse SP-API offers response into standardized format.

        Parameters
        ----------
        payload : Dict[str, Any]
            Raw API response payload

        Returns
        -------
        List[Dict[str, Any]]
            Parsed offer data
        """
        offers = []

        raw_offers = payload.get("Offers", [])

        for offer in raw_offers:
            try:
                # Extract listing price
                listing_price_data = offer.get("ListingPrice", {})
                listing_price = float(listing_price_data.get("Amount", 0))

                # Extract shipping cost
                shipping_data = offer.get("Shipping", {})
                shipping_cost = float(shipping_data.get("Amount", 0))

                # Extract seller feedback
                feedback_data = offer.get("SellerFeedbackRating", {})
                seller_rating = feedback_data.get("SellerPositiveFeedbackRating")
                feedback_count = feedback_data.get("FeedbackCount", 0)

                # Extract shipping time
                shipping_time = offer.get("ShippingTime", {})
                max_hours = shipping_time.get("maximumHours", 0)
                availability = shipping_time.get("availabilityType", "UNKNOWN")

                # Extract Prime info
                prime_info = offer.get("PrimeInformation", {})
                is_prime = prime_info.get("IsPrime", False)

                offers.append({
                    "seller_id": offer.get("SellerId", "Unknown"),
                    "listing_price": listing_price,
                    "shipping_cost": shipping_cost,
                    "is_buy_box_winner": offer.get("IsBuyBoxWinner", False),
                    "is_fba": offer.get("IsFulfilledByAmazon", False),
                    "is_prime": is_prime,
                    "seller_rating": seller_rating,
                    "feedback_count": feedback_count,
                    "availability": availability,
                    "max_shipping_hours": max_hours
                })

            except Exception as e:
                self.logger.warning(f"Failed to parse offer: {e}")

        return offers

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((SellingApiException,))
    )
    def get_product_name(self, asin: str) -> str:
        """
        Get product name/title for an ASIN.

        Parameters
        ----------
        asin : str
            Amazon Standard Identification Number

        Returns
        -------
        str
            Product title, or "Unknown" if not found
        """
        self._catalog_limiter.acquire()

        try:
            catalog_api = self._get_catalog_api()
            response = catalog_api.get_catalog_item(
                asin=asin,
                marketplaceIds=[self.MARKETPLACE_US],
                includedData=["summaries"]
            )

            # Extract product name from summaries
            summaries: List[Dict[str, Any]] = response.payload.get("summaries", [])
            for summary in summaries:
                if summary.get("marketplaceId") == self.MARKETPLACE_US:
                    item_name = summary.get("itemName", "Unknown")
                    return str(item_name) if item_name else "Unknown"

            # Fallback to first summary if US not found
            if summaries:
                item_name = summaries[0].get("itemName", "Unknown")
                return str(item_name) if item_name else "Unknown"

            return "Unknown"

        except SellingApiException as e:
            if e.code == 404:
                self.logger.warning(f"Product not found: {asin}")
                return "Product not found"
            self.logger.error(f"Failed to get product name for {asin}: {e}")
            raise

    def get_item_offers_batch(self, asins: List[str]) -> List[Dict[str, Any]]:
        """
        Get offers for multiple ASINs.

        Parameters
        ----------
        asins : List[str]
            List of ASINs to fetch

        Returns
        -------
        List[Dict[str, Any]]
            List of results for each ASIN
        """
        results = []

        for asin in asins:
            try:
                offers = self.get_item_offers(asin)
                product_name = self.get_product_name(asin)
                results.append({
                    "asin": asin,
                    "product_name": product_name,
                    "offers": offers,
                    "error": None
                })
            except Exception as e:
                results.append({
                    "asin": asin,
                    "product_name": "Unknown",
                    "offers": [],
                    "error": str(e)
                })

        return results
