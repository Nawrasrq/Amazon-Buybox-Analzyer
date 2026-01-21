# Claude Project Guide: Amazon Buy Box Analyzer

## Project Context

This is an **Amazon Buy Box Analyzer** tool that uses the Amazon Selling Partner API (SP-API) to analyze Buy Box winners for given ASINs. It provides a Tkinter GUI for credential management and ASIN input, and outputs formatted Excel reports.

**Key Capabilities:**
- Connect to Amazon SP-API (Pricing and Catalog APIs)
- Analyze Buy Box winners and determine winning factors
- Export results to formatted Excel files
- Manage SP-API credentials via GUI or .env file

## Architecture Overview

### Core Design Patterns

1. **Abstract Base Class Pattern**
   - `Base` class provides logging infrastructure and utility initialization
   - `BuyBoxAnalyzer` extends Base with ETL methods for Buy Box analysis
   - Parameterless abstract methods (`extract`, `transform`, `load`, `main`) with instance variables

2. **Instance-Specific Logging**
   - Multiple instances can run simultaneously with separate log files
   - Each instance gets unique loggers (e.g., `scripts.buybox_analyzer.instance_1`)

3. **Utility Composition**
   - `API` utility handles SP-API communication with rate limiting
   - `File` utility handles Excel export and .env file operations

4. **ETL Pattern with Convenience Method**
   - Abstract methods have no parameters (read from instance variables)
   - `run(asins, output_path)` convenience method sets variables and calls `main()`

### Directory Structure

```
Amazon Buybox Analyzer/
├── main/                        # Entry points
│   ├── main.py                  # CLI entry point
│   ├── main.bat                 # Windows CLI launcher
│   ├── tool.py                  # GUI entry point
│   └── tool.bat                 # Windows GUI launcher
├── scripts/                     # Core classes
│   ├── base.py                  # Abstract base class with logging
│   └── buybox_analyzer.py       # Main analyzer (ETL implementation)
├── utils/                       # Utility classes
│   ├── api.py                   # SP-API client with rate limiting
│   └── file.py                  # Excel export, .env operations
├── tools/                       # GUI application
│   └── tool.py                  # Tkinter GUI with tabs
├── config/                      # Configuration
│   └── marketplaces.py          # Amazon marketplace constants
├── tests/                       # Unit tests
│   ├── conftest.py              # Pytest fixtures
│   ├── test_buybox_analyzer.py  # Analyzer tests
│   ├── test_api.py              # API utility tests
│   └── test_file.py             # File utility tests
├── logs/                        # Application logs
├── output/                      # Excel output files
├── env.example                  # Environment variable template
├── requirements.txt             # Python dependencies
├── LICENSE                      # MIT License
└── README.md                    # User documentation
```

## Core Components

### 1. Base Class (`scripts/base.py`)

**Purpose:** Abstract base class providing logging and utility initialization.

**Key Features:**
- Instance-specific logging with unique IDs
- Initializes `API` and `File` utilities
- Abstract ETL methods: `extract()`, `transform()`, `load()`, `main()`
- `dispose()` method for cleanup

**CRITICAL: `base_modules` List**
```python
base_modules = ['scripts.base', 'scripts.buybox_analyzer', 'utils.api', 'utils.file', 'tools.tool']
```

### 2. BuyBoxAnalyzer Class (`scripts/buybox_analyzer.py`)

**Purpose:** Main analyzer that fetches SP-API data and determines Buy Box winners.

**Key Classes:**
- `OfferData` - Dataclass representing a seller's offer
- `BuyBoxResult` - Dataclass representing analysis results for one ASIN
- `BuyBoxAnalyzer` - Main ETL class

**ETL Flow:**
```python
# Instance variables set before ETL methods
self._asins: List[str] = []        # Input ASINs
self._output_path: str = ""         # Output Excel path

# ETL methods (parameterless, use instance variables)
def extract(self) -> None:          # Fetches data from SP-API
def transform(self) -> None:        # Parses offers, determines winners
def load(self) -> str:              # Exports to Excel

# Convenience method
def run(asins, output_path) -> Dict:  # Sets variables, calls main()
```

**Analysis Factors:**
- Price comparison (lowest or within 2%)
- FBA/Prime status
- Seller rating (95%+ excellent, 90%+ good)
- Feedback volume (10K+ high, 1K+ strong)
- Availability and shipping speed

### 3. API Utility (`utils/api.py`)

**Purpose:** SP-API client with rate limiting and retry logic.

**Key Features:**
- `RateLimiter` class with token bucket algorithm
- Separate rate limits for Pricing (0.5 req/s) and Catalog (2 req/s) APIs
- Credential management via `configure()` method
- Retry logic with tenacity for transient errors

**Key Methods:**
```python
def configure(refresh_token, client_id, client_secret)  # Set credentials
def test_connection() -> bool                           # Verify credentials
def get_item_offers(asin) -> List[Dict]                 # Get offers for ASIN
def get_product_name(asin) -> str                       # Get product title
```

### 4. File Utility (`utils/file.py`)

**Purpose:** Excel export and .env file operations.

**Key Methods:**
```python
def write_buybox_excel(results, output_path) -> str     # Export to Excel
def read_env_file(path) -> Dict[str, str]               # Read .env
def update_env_file(values, path)                       # Update .env
def get_default_output_path() -> str                    # Generate output path
```

### 5. GUI Tool (`tools/tool.py`)

**Purpose:** Tkinter GUI with credential management and analysis interface.

**Key Features:**
- Two tabs: Credentials and Analyze
- Credential fields with show/hide toggle
- Test Connection button
- Save to .env functionality
- ASIN text area (newline-separated)
- Progress bar and status updates
- Background threading for non-blocking UI

**Thread Safety:**
Uses `root.after(0, callback, args)` for thread-safe UI updates.

## Code Standards

### Type Hints

All method signatures include type annotations:
```python
def run(self, asins: List[str], output_path: str) -> Dict[str, Any]:
```

### Docstring Format

NumPy-style docstrings:
```python
def method(self, param: str) -> str:
    """
    Short description.

    Parameters
    ----------
    param : str
        Parameter description

    Returns
    -------
    str
        Return value description

    Raises
    ------
    ValueError
        When raised
    """
```

### Error Handling

- Guard clauses at method start for required variables
- Try-except blocks with logging before re-raising
- Specific exception types where possible

### Method Organization

```python
class BuyBoxAnalyzer(Base):
    # MARK: Initialization
    def __init__(self, file_path: str):

    # MARK: Configuration
    def set_progress_callback(self, callback):

    # MARK: ETL Methods
    def extract(self) -> None:
    def transform(self) -> None:
    def load(self) -> str:
    def main(self) -> Dict[str, Any]:
    def run(self, asins, output_path) -> Dict[str, Any]:

    # MARK: Analysis Methods
    def _parse_offers(self, offers_data):
    def _analyze_offers(self, offers, asin, product_name):
    def _determine_reasons(self, winner, all_offers):
```

## Environment Variables

```env
# SP-API Credentials
SP_API_REFRESH_TOKEN=your_refresh_token
SP_API_CLIENT_ID=your_client_id
SP_API_CLIENT_SECRET=your_client_secret

# Marketplace
SP_API_MARKETPLACE_ID=ATVPDKIKX0DER

# File Paths
OUTPUT_PATH=./output
```

## Testing

### Test Structure

```
tests/
├── conftest.py               # Shared fixtures
├── test_buybox_analyzer.py   # Analyzer tests
├── test_api.py               # API utility tests
└── test_file.py              # File utility tests
```

### Key Fixtures (conftest.py)

- `analyzer_instance` - BuyBoxAnalyzer with cleanup
- `api_instance` - API utility
- `file_instance` - File utility with temp directory
- `sample_offers` - List of OfferData objects
- `sample_buybox_results` - List of BuyBoxResult objects
- `temp_directory` - Temporary directory with cleanup

### Running Tests

```bash
pytest                           # Run all tests
pytest -v                        # Verbose output
pytest tests/test_api.py         # Specific file
pytest --cov=scripts --cov=utils # With coverage
```

## Common Tasks

### Adding a New Analysis Factor

1. Update `_determine_reasons()` in `buybox_analyzer.py`
2. Add new field to `OfferData` if needed
3. Update `_parse_offers()` to extract the data
4. Add tests in `test_buybox_analyzer.py`

### Modifying Excel Output

1. Update `write_buybox_excel()` in `utils/file.py`
2. Add/modify columns in the data dictionary
3. Update column widths and formatting as needed
4. Update tests in `test_file.py`

### Adding a New Marketplace

1. Add marketplace constant to `config/marketplaces.py`
2. Update GUI dropdown if adding marketplace selection
3. Pass marketplace ID to API methods

## Dependencies

```
python-amazon-sp-api>=1.0.0    # SP-API client
pandas>=1.5.0                   # Data manipulation
xlsxwriter>=3.0.0               # Excel export
python-dotenv>=0.19.0           # Environment variables
tenacity>=8.0.0                 # Retry logic
pytest>=7.0.0                   # Testing
```

## Troubleshooting

### SP-API Connection Issues
- Verify credentials are correct
- Check that app has required permissions (Pricing, Catalog)
- Ensure refresh token hasn't expired

### Rate Limiting Errors
- Built-in rate limiting should handle this
- If seeing 429 errors, reduce request frequency

### GUI Not Responding
- Analysis runs in background thread
- Check logs for errors if stuck

### Excel Export Errors
- Ensure output directory exists or is writable
- Check for file locks if overwriting existing file
