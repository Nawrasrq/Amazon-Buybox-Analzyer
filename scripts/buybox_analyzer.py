# Buy Box Analyzer - Core analysis logic for Amazon Buy Box determination
# Inherits from Base class for logging infrastructure
# Analyzes offer data to determine Buy Box winners and reasons

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from scripts.base import Base


@dataclass
class OfferData:
    """
    Represents a single seller offer for an ASIN.

    Parameters
    ----------
    seller_id : str
        Amazon seller identifier
    listing_price : float
        Product listing price in USD
    shipping_cost : float
        Shipping cost in USD
    is_buy_box_winner : bool
        Whether this offer currently has the Buy Box
    is_fba : bool
        Whether fulfilled by Amazon
    is_prime : bool
        Whether Prime eligible
    seller_rating : Optional[float]
        Seller positive feedback percentage (0-100)
    feedback_count : int
        Total number of seller feedback ratings
    availability : str
        Stock availability status (e.g., "NOW", "FUTURE")
    max_shipping_hours : int
        Maximum shipping time in hours
    """
    seller_id: str
    listing_price: float
    shipping_cost: float
    is_buy_box_winner: bool
    is_fba: bool
    is_prime: bool
    seller_rating: Optional[float]
    feedback_count: int
    availability: str
    max_shipping_hours: int

    @property
    def total_price(self) -> float:
        """Calculate total price including shipping."""
        return self.listing_price + self.shipping_cost


@dataclass
class BuyBoxResult:
    """
    Analysis result for a single ASIN.

    Parameters
    ----------
    asin : str
        Amazon Standard Identification Number
    product_name : str
        Product title from catalog
    winner_seller_id : Optional[str]
        Seller ID of Buy Box winner, or None if no winner
    winner_price : Optional[float]
        Winner's listing price
    winner_shipping : Optional[float]
        Winner's shipping cost
    winner_total_price : Optional[float]
        Winner's total price (listing + shipping)
    winner_is_fba : Optional[bool]
        Whether winner is FBA
    winner_is_prime : Optional[bool]
        Whether winner is Prime eligible
    winner_seller_rating : Optional[float]
        Winner's seller rating percentage
    reasons : List[str]
        List of reasons why the winner got the Buy Box
    total_offers : int
        Total number of competing offers
    analysis_timestamp : datetime
        When the analysis was performed
    error : Optional[str]
        Error message if analysis failed for this ASIN
    """
    asin: str
    product_name: str
    winner_seller_id: Optional[str]
    winner_price: Optional[float]
    winner_shipping: Optional[float]
    winner_total_price: Optional[float]
    winner_is_fba: Optional[bool]
    winner_is_prime: Optional[bool]
    winner_seller_rating: Optional[float]
    reasons: List[str]
    total_offers: int
    analysis_timestamp: datetime
    error: Optional[str] = None


class BuyBoxAnalyzer(Base):
    """
    Analyzes Amazon Buy Box winners for given ASINs.

    Inherits from Base class to get logging infrastructure and utility access.
    Uses SP-API to fetch offer data and analyzes factors that determine
    Buy Box winners.
    """

    def __init__(self, file_path: str):
        """
        Initialize the Buy Box Analyzer.

        Parameters
        ----------
        file_path : str
            Path to log file relative to logs/ directory
        """
        super().__init__(file_path=file_path)
        logger_name = f"scripts.buybox_analyzer.instance_{self.instance_id}"
        self.logger = logging.getLogger(logger_name)

        self.raw_data: List[Dict[str, Any]] = []
        self.results: List[BuyBoxResult] = []
        self.progress_callback: Optional[Callable[[int, int, str], None]] = None

        # ETL parameters (set before calling extract/load)
        self._asins: List[str] = []
        self._output_path: str = ""

        self.logger.info("Initialized BuyBoxAnalyzer class")

    # MARK: Configuration
    def set_progress_callback(self, callback: Callable[[int, int, str], None]) -> None:
        """
        Set callback function for progress updates.

        Parameters
        ----------
        callback : Callable[[int, int, str], None]
            Function that receives (current, total, message)
        """
        self.progress_callback = callback

    def _update_progress(self, current: int, total: int, message: str) -> None:
        """
        Send progress update via callback if set.

        Parameters
        ----------
        current : int
            Current item number
        total : int
            Total number of items
        message : str
            Status message
        """
        if self.progress_callback:
            self.progress_callback(current, total, message)

    # MARK: ETL Methods
    def extract(self) -> None:
        """
        Extract offer and catalog data from SP-API for each ASIN.

        Uses self._asins which must be set before calling this method.

        Raises
        ------
        ValueError
            If _asins is empty or not set
        """
        try:
            if not self._asins:
                raise ValueError("No ASINs provided. Set _asins before calling extract().")

            asins = self._asins
            self.logger.info(f"Starting extraction for {len(asins)} ASINs")
            self.raw_data = []

            for i, asin in enumerate(asins, 1):
                self._update_progress(i, len(asins), f"Fetching data for {asin}")
                self.logger.info(f"Fetching data for ASIN {asin} ({i}/{len(asins)})")

                try:
                    # Get product name from catalog API
                    product_name = self.api.get_product_name(asin)

                    # Get offers from pricing API
                    offers_data = self.api.get_item_offers(asin)

                    self.raw_data.append({
                        "asin": asin,
                        "product_name": product_name,
                        "offers": offers_data,
                        "error": None
                    })

                    self.logger.info(f"Found {len(offers_data)} offers for {asin}")

                except Exception as e:
                    self.logger.warning(f"Failed to fetch data for {asin}: {e}")
                    self.raw_data.append({
                        "asin": asin,
                        "product_name": "Unknown",
                        "offers": [],
                        "error": str(e)
                    })

            self.logger.info(f"Extraction complete: {len(self.raw_data)} ASINs processed")

        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            raise

    def transform(self) -> None:
        """
        Transform raw API data into BuyBoxResult objects.

        Parses offers and applies analysis algorithm to determine
        Buy Box winners and reasons.

        Raises
        ------
        ValueError
            If raw_data is empty (extract() not called or failed)
        """
        try:
            if not self.raw_data:
                raise ValueError("No raw data to transform. Call extract() first.")

            self.logger.info("Starting transformation")
            self.results = []

            for data in self.raw_data:
                asin = data["asin"]
                product_name = data["product_name"]
                error = data["error"]

                if error:
                    # Create error result
                    self.results.append(BuyBoxResult(
                        asin=asin,
                        product_name=product_name,
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
                        error=error
                    ))
                    continue

                # Parse offers into OfferData objects
                offers = self._parse_offers(data["offers"])

                # Analyze offers
                result = self._analyze_offers(offers, asin, product_name)
                self.results.append(result)

            self.logger.info(f"Transformation complete: {len(self.results)} results")

        except Exception as e:
            self.logger.error(f"Transformation failed: {e}")
            raise

    def load(self) -> str:
        """
        Export analysis results to Excel file.

        Uses self._output_path which must be set before calling this method.

        Returns
        -------
        str
            Path to the created Excel file

        Raises
        ------
        ValueError
            If _output_path is empty or results is empty
        """
        try:
            if not self._output_path:
                raise ValueError("No output path provided. Set _output_path before calling load().")
            if not self.results:
                raise ValueError("No results to export. Call extract() and transform() first.")

            output_path = self._output_path
            self.logger.info(f"Saving results to {output_path}")
            result_path = self.file.write_buybox_excel(self.results, output_path)
            self.logger.info("Results saved successfully")
            return result_path

        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")
            raise

    def main(self) -> Dict[str, Any]:
        """
        Main orchestration method for Buy Box analysis.

        Uses self._asins and self._output_path which must be set before calling.
        For convenience, use run(asins, output_path) instead.

        Returns
        -------
        Dict[str, Any]
            Dictionary with status, output_path, and count

        Raises
        ------
        ValueError
            If _asins or _output_path are not set
        """
        try:
            if not self._asins:
                raise ValueError("No ASINs provided. Set _asins before calling main().")
            if not self._output_path:
                raise ValueError("No output path provided. Set _output_path before calling main().")

            self.logger.info(f"Starting Buy Box analysis for {len(self._asins)} ASINs")

            # Execute ETL pipeline
            self.extract()
            self.transform()
            result_path = self.load()

            success_count = sum(1 for r in self.results if r.error is None)
            error_count = sum(1 for r in self.results if r.error is not None)

            self.logger.info(f"Analysis complete: {success_count} successful, {error_count} errors")

            return {
                "status": "success",
                "output_path": result_path,
                "total_count": len(self.results),
                "success_count": success_count,
                "error_count": error_count
            }

        except Exception as e:
            self.logger.error(f"Buy Box analysis failed: {e}")
            raise

    def run(self, asins: List[str], output_path: str) -> Dict[str, Any]:
        """
        Convenience method to run Buy Box analysis with parameters.

        Sets the required instance variables and calls main().

        Parameters
        ----------
        asins : List[str]
            List of ASINs to analyze
        output_path : str
            Path for output Excel file

        Returns
        -------
        Dict[str, Any]
            Dictionary with status, output_path, and count
        """
        self._asins = asins
        self._output_path = output_path
        return self.main()

    # MARK: Analysis Methods
    def _parse_offers(self, offers_data: List[Dict[str, Any]]) -> List[OfferData]:
        """
        Parse raw API offer data into OfferData objects.

        Parameters
        ----------
        offers_data : List[Dict[str, Any]]
            Raw offer data from SP-API

        Returns
        -------
        List[OfferData]
            Parsed offer objects
        """
        offers = []

        for offer in offers_data:
            try:
                offers.append(OfferData(
                    seller_id=offer.get("seller_id", "Unknown"),
                    listing_price=offer.get("listing_price", 0.0),
                    shipping_cost=offer.get("shipping_cost", 0.0),
                    is_buy_box_winner=offer.get("is_buy_box_winner", False),
                    is_fba=offer.get("is_fba", False),
                    is_prime=offer.get("is_prime", False),
                    seller_rating=offer.get("seller_rating"),
                    feedback_count=offer.get("feedback_count", 0),
                    availability=offer.get("availability", "UNKNOWN"),
                    max_shipping_hours=offer.get("max_shipping_hours", 0)
                ))
            except Exception as e:
                self.logger.warning(f"Failed to parse offer: {e}")

        return offers

    def _analyze_offers(self, offers: List[OfferData], asin: str, product_name: str) -> BuyBoxResult:
        """
        Analyze offers and determine Buy Box winner with reasons.

        Parameters
        ----------
        offers : List[OfferData]
            List of parsed offers
        asin : str
            ASIN being analyzed
        product_name : str
            Product name

        Returns
        -------
        BuyBoxResult
            Analysis result with winner and reasons
        """
        # Find the Buy Box winner
        winner = next((o for o in offers if o.is_buy_box_winner), None)

        if not winner:
            return BuyBoxResult(
                asin=asin,
                product_name=product_name,
                winner_seller_id=None,
                winner_price=None,
                winner_shipping=None,
                winner_total_price=None,
                winner_is_fba=None,
                winner_is_prime=None,
                winner_seller_rating=None,
                reasons=["No Buy Box winner found"],
                total_offers=len(offers),
                analysis_timestamp=datetime.now(),
                error=None
            )

        # Determine reasons for winning
        reasons = self._determine_reasons(winner, offers)

        return BuyBoxResult(
            asin=asin,
            product_name=product_name,
            winner_seller_id=winner.seller_id,
            winner_price=winner.listing_price,
            winner_shipping=winner.shipping_cost,
            winner_total_price=winner.total_price,
            winner_is_fba=winner.is_fba,
            winner_is_prime=winner.is_prime,
            winner_seller_rating=winner.seller_rating,
            reasons=reasons,
            total_offers=len(offers),
            analysis_timestamp=datetime.now(),
            error=None
        )

    def _determine_reasons(self, winner: OfferData, all_offers: List[OfferData]) -> List[str]:
        """
        Determine reasons why the winner got the Buy Box.

        Analyzes price, fulfillment, seller rating, and other factors.

        Parameters
        ----------
        winner : OfferData
            The winning offer
        all_offers : List[OfferData]
            All competing offers

        Returns
        -------
        List[str]
            List of reasons explaining the win
        """
        reasons = []

        # Price comparison
        all_prices = [o.total_price for o in all_offers]
        min_price = min(all_prices) if all_prices else 0

        if winner.total_price == min_price:
            reasons.append(f"Lowest total price (${winner.total_price:.2f})")
        elif min_price > 0 and winner.total_price <= min_price * 1.02:
            reasons.append(f"Competitive price within 2% of lowest (${winner.total_price:.2f})")

        # Prime/FBA status
        if winner.is_fba:
            reasons.append("Fulfilled by Amazon (FBA)")
        if winner.is_prime:
            reasons.append("Prime eligible")

        # Seller rating
        if winner.seller_rating is not None:
            if winner.seller_rating >= 95:
                reasons.append(f"Excellent seller rating ({winner.seller_rating:.0f}%)")
            elif winner.seller_rating >= 90:
                reasons.append(f"Good seller rating ({winner.seller_rating:.0f}%)")

        # Feedback volume
        if winner.feedback_count >= 10000:
            reasons.append(f"High feedback volume ({winner.feedback_count:,} ratings)")
        elif winner.feedback_count >= 1000:
            reasons.append(f"Strong feedback volume ({winner.feedback_count:,} ratings)")

        # Availability
        if winner.availability == "NOW":
            reasons.append("In stock and ready to ship")

        # Shipping speed
        if winner.max_shipping_hours > 0 and winner.max_shipping_hours <= 48:
            reasons.append(f"Fast shipping ({winner.max_shipping_hours}h max)")

        # Default reason if none determined
        if not reasons:
            reasons.append("Buy Box winner by Amazon algorithm")

        return reasons
