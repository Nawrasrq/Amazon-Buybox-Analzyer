# Amazon Buy Box Analyzer

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A Python tool that analyzes Amazon Buy Box winners using the Amazon Selling Partner API (SP-API). Input a list of ASINs and get an Excel report with product details, Buy Box winners, and analysis of why each seller won the Buy Box.

## Features

- **SP-API Integration**: Connects to Amazon's Selling Partner API for real-time data
- **Buy Box Analysis**: Identifies current Buy Box winners and analyzes contributing factors
- **Tkinter GUI**: User-friendly interface with credential management and progress tracking
- **Excel Export**: Formatted reports with Amazon-styled headers
- **Rate Limiting**: Built-in rate limiting to comply with SP-API quotas

## Project Structure

```
Amazon Buybox Analyzer/
├── main/                    # Entry points
│   ├── main.py              # CLI entry point
│   └── tool.py              # GUI entry point
├── scripts/                 # Core classes
│   ├── base.py              # Abstract base class
│   └── buybox_analyzer.py   # Main analyzer implementation
├── utils/                   # Utilities
│   ├── api.py               # SP-API client with rate limiting
│   └── file.py              # Excel export and .env operations
├── tools/                   # GUI application
│   └── tool.py              # Tkinter GUI implementation
├── config/                  # Configuration
│   └── marketplaces.py      # Amazon marketplace constants
├── tests/                   # Unit tests
│   ├── conftest.py          # Pytest fixtures
│   ├── test_buybox_analyzer.py
│   ├── test_api.py
│   └── test_file.py
└── logs/                    # Application logs
```

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Amazon SP-API credentials (Refresh Token, Client ID, Client Secret)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Amazon Buybox Analyzer"
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure credentials** (optional - can also be done via GUI)
   ```bash
   cp env.example .env
   # Edit .env with your SP-API credentials
   ```

### Usage

#### GUI Mode (Recommended)

```bash
python main/tool.py
# or
main/tool.bat
```

1. Open the **Credentials** tab
2. Enter your SP-API credentials (Refresh Token, Client ID, Client Secret)
3. Click **Test Connection** to verify
4. Optionally click **Save to .env** to persist credentials
5. Switch to the **Analyze** tab
6. Paste ASINs (one per line) into the text area
7. Click **Analyze Buy Box** to start
8. Results are saved to an Excel file in the `output/` directory

#### CLI Mode

```bash
python main/main.py
```

Edit `main/main.py` to customize the list of ASINs to analyze.

## SP-API Setup

To use this tool, you need Amazon SP-API credentials:

1. **Register as a Developer** on Amazon Seller Central
2. **Create an App** in the Developer Console
3. **Get Credentials**:
   - **LWA Client ID**: From your app settings
   - **LWA Client Secret**: From your app settings
   - **Refresh Token**: Generated through the authorization process

### Required SP-API Permissions

- **Product Listing**: For catalog data (product names)
- **Pricing**: For offer data and Buy Box information

## Output Format

The Excel report includes:

| Column | Description |
|--------|-------------|
| ASIN | Amazon Standard Identification Number |
| Product Name | Product title from catalog |
| Buy Box Winner | Seller ID of current winner |
| Price | Winner's listing price |
| Shipping | Winner's shipping cost |
| Total Price | Combined price + shipping |
| FBA | Whether winner uses Fulfillment by Amazon |
| Prime | Whether winner is Prime eligible |
| Seller Rating | Winner's feedback percentage |
| Reasons | Analysis of why they won the Buy Box |
| Total Offers | Number of competing sellers |
| Error | Any errors encountered |

## Buy Box Analysis Factors

The analyzer evaluates these factors to explain Buy Box wins:

- **Price**: Lowest or competitive total price (within 2% of lowest)
- **Fulfillment**: FBA (Fulfilled by Amazon) status
- **Prime**: Prime eligibility
- **Seller Rating**: Feedback percentage (Excellent: 95%+, Good: 90%+)
- **Feedback Volume**: Number of ratings (High: 10,000+, Strong: 1,000+)
- **Availability**: In-stock status
- **Shipping Speed**: Fast shipping (48 hours or less)

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# SP-API Credentials
SP_API_REFRESH_TOKEN=your_refresh_token
SP_API_CLIENT_ID=your_client_id
SP_API_CLIENT_SECRET=your_client_secret

# Marketplace (US by default)
SP_API_MARKETPLACE_ID=ATVPDKIKX0DER

# File Paths
OUTPUT_PATH=./output
```

### Rate Limits

The tool includes built-in rate limiting:
- **Pricing API**: 0.5 requests/second (burst: 1)
- **Catalog API**: 2 requests/second (burst: 2)

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_buybox_analyzer.py

# Run with coverage
pytest --cov=scripts --cov=utils
```

## Dependencies

- `python-amazon-sp-api` - Amazon SP-API client
- `pandas` - Data manipulation
- `xlsxwriter` - Excel file creation
- `python-dotenv` - Environment variable management
- `tenacity` - Retry logic for API calls
- `pytest` - Testing framework

## License

MIT License - see [LICENSE](LICENSE) for details.

## Resources

- [Amazon SP-API Documentation](https://developer-docs.amazon.com/sp-api/)
- [python-amazon-sp-api](https://github.com/saleweaver/python-amazon-sp-api)
