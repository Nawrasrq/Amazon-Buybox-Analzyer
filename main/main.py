# Entry point for Amazon Buy Box Analyzer (CLI mode)
# Use main/tool.py for GUI mode instead

from scripts.buybox_analyzer import BuyBoxAnalyzer


def main():
    """
    Main function for CLI-based analysis.

    For GUI mode, run main/tool.py instead.
    """
    # Example usage - replace with actual ASINs
    sample_asins = [
        "B08N5WRWNW",
        "B07XJ8C8F5"
    ]

    analyzer = BuyBoxAnalyzer('analyzer/analyzer.log')
    try:
        result = analyzer.run(sample_asins, "output/buybox_analysis.xlsx")
        print(f"Analysis complete: {result}")
    finally:
        analyzer.dispose()


if __name__ == "__main__":
    main()
