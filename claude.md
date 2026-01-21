# Claude Project Guide: Python OOB Template

## Project Context

This is an **Object-Oriented Base (OOB) Python Project Template** designed for ETL (Extract, Transform, Load) processes, automation workflows, API integrations, and data processing applications. It provides a structured foundation with proper logging, error handling, and modular design patterns.

**Use this template for projects involving:**
- Database operations (reading/writing to SQL databases)
- API integrations and data consumption
- File processing (CSV, Excel, text files)
- Data transformation pipelines
- GUI tools for manual operations
- Scheduled automation processes

## Architecture Overview

### Core Design Patterns

1. **Abstract Base Class Pattern**
   - `Base` class provides common functionality and enforces structure
   - Child classes implement abstract methods (extract, transform, load, main)
   - Inheritance chain passes configuration (e.g., log file paths)

2. **Instance-Specific Logging**
   - Multiple instances can run simultaneously with separate log files
   - Each instance gets unique loggers (e.g., `scripts.child.instance_1`)
   - Hierarchical logger naming preserves module structure

3. **Utility Composition**
   - Base class initializes utility objects (DB, API, File)
   - Utilities receive instance IDs for isolated logging
   - Wrapper methods provide clean access to utility functions

4. **Resource Management**
   - Explicit `dispose()` method for cleanup
   - Proper handler removal and file closure
   - Context-aware error handling

### Directory Structure

```
📁 Project Root
├── 📁 main/           # Entry points and batch files
│   ├── main.py        # Primary execution script
│   ├── main.bat       # Windows automation launcher
│   ├── tool.py        # GUI tool entry point
│   └── tool.bat       # Tool launcher with environment setup
├── 📁 scripts/        # Core classes (Base & Child implementations)
│   ├── base.py        # Abstract base class
│   └── child.py       # Concrete implementation
├── 📁 utils/          # Utility classes
│   ├── db.py          # Database operations
│   ├── api.py         # API interactions
│   └── file.py        # File processing
├── 📁 tools/          # GUI tools and manual operations
│   └── tool.py        # Tool class with GUI integration
├── 📁 tests/          # Unit tests
│   ├── conftest.py    # Pytest fixtures
│   ├── test_child.py  # Child class tests
│   └── test_db_utils.py  # Database utility tests
├── 📁 config/         # Configuration files and mappings
├── 📁 docs/           # Documentation and schemas
│   └── schema.sql     # Database schema definitions
├── 📁 logs/           # Application logs (organized by module)
├── .env.example      # Environment variable template
├── .gitignore         # Git ignore patterns
├── requirements.txt   # Python dependencies
└── README.md          # Comprehensive documentation
```

## Core Components

### 1. Base Class (`scripts/base.py`)

**Purpose:** Abstract base class that provides common functionality for all child classes.

**Key Responsibilities:**
- Configure instance-specific logging system
- Initialize utility objects (DB, API, File) with instance IDs
- Provide wrapper methods for utility access
- Enforce implementation of abstract ETL methods
- Manage resource disposal

**Critical Implementation Details:**

```python
class Base(abc.ABC):
    _instance_count = 0  # Class-level counter for unique instances

    def __init__(self, file_path: str):
        # Increment instance counter and assign unique ID
        Base._instance_count += 1
        self.instance_id = Base._instance_count

        # Setup logging with instance-specific loggers
        self.configure_logging(file_path=file_path)

        # Initialize utilities with instance ID
        self.db = DB(instance_id=self.instance_id)
        self.api = API(instance_id=self.instance_id)
        self.file = File(instance_id=self.instance_id)
```

**CRITICAL: `base_modules` List**
When adding/removing utility classes or renaming script files, update this list in `configure_logging()` and `dispose()`:

```python
base_modules = ['scripts.base', 'scripts.child', 'utils.api', 'utils.file', 'utils.db', 'tools.tool']
```

**Abstract Methods to Implement:**
- `extract()` - Extract data from source systems
- `transform()` - Transform extracted data
- `load()` - Load transformed data to destination
- `main()` - Main execution orchestrator

### 2. Child Class (`scripts/child.py`)

**Purpose:** Concrete implementation of Base class with specific business logic.

**Implementation Pattern:**

```python
class Child(Base):
    def __init__(self, file_path: str):
        # Initialize base class first
        super().__init__(file_path=file_path)

        # Get instance-specific logger
        logger_name = f"scripts.child.instance_{self.instance_id}"
        self.logger = logging.getLogger(logger_name)

        # Add child-specific initialization here

    def extract(self):
        """Extract data from source systems."""
        try:
            self.logger.info("Starting data extraction")
            # Implementation here
        except Exception as e:
            self.logger.error(f"Data extraction failed: {e}")
            raise

    # Implement transform(), load(), main() following same pattern
```

**Key Points:**
- Always call `super().__init__()` first
- Use instance-specific logger naming pattern
- Wrap all methods in try-except with logging
- Log meaningful metrics (row counts, processing times)
- Return structured data from `main()` method

### 3. Utility Classes (`utils/`)

**Purpose:** Reusable classes for common operations.

**Common Pattern:**

```python
class DB:
    def __init__(self, instance_id=None):
        # Setup instance-specific logging
        if instance_id:
            logger_name = f"utils.db.instance_{instance_id}"
        else:
            logger_name = "utils.db"
        self.logger = logging.getLogger(logger_name)

        # Initialize resources
        self._engines: Dict[str, Engine] = {}
```

**Available Utilities:**
- **DB (`utils/db.py`)** - Database operations with SQLAlchemy
  - Connection pooling for multiple databases
  - DataFrame read/write operations
  - Bulk insert and upsert capabilities
  - Change detection filtering

- **API (`utils/api.py`)** - HTTP/REST API interactions
  - GET, POST, PUT, DELETE operations
  - Authentication management
  - Retry logic with backoff

- **File (`utils/file.py`)** - File processing
  - CSV, Excel, text file handling
  - Data validation
  - File management (archive, cleanup)

### 4. Tools (`tools/tool.py`)

**Purpose:** GUI applications or interactive tools for manual operations.

**Integration Pattern:**

```python
class Tool:
    def __init__(self, log_file_path: str = "tool/tool.log"):
        # Create Child instance for script integration
        self.child = Child(log_file_path)

        # Get instance-specific logger
        tool_logger_name = f"tools.tool.instance_{self.child.instance_id}"
        self.logger = logging.getLogger(tool_logger_name)

        # Create GUI
        self.create_gui()

    def dispose(self):
        """Dispose of tool resources."""
        if hasattr(self, 'child') and self.child:
            self.child.dispose()
```

**Key Features:**
- Optional Child class integration
- Default log file location with sensible defaults
- Proper resource cleanup via `dispose()`

### 5. Main Entry Point (`main/main.py`)

**Purpose:** Execute automation scripts with proper initialization and cleanup.

**Standard Pattern:**

```python
def main():
    """Main function"""
    # Instance 1
    child_1 = Child('child/child_1.log')
    child_1.main()
    child_1.dispose()

    # Instance 2 (separate log file)
    child_2 = Child('child/child_2.log')
    child_2.main()
    child_2.dispose()

if __name__ == "__main__":
    main()
```

**Key Points:**
- Always call `dispose()` after execution
- Use separate log files for concurrent instances
- Organize logs by purpose (e.g., 'child/', 'tool/')

## Instance-Specific Logging System

### How It Works

The logging system enables multiple script instances to run simultaneously with isolated log files while maintaining clear hierarchical logger naming.

**Example Logger Names:**
- `scripts.base.instance_1`
- `scripts.child.instance_1`
- `utils.db.instance_1`
- `utils.api.instance_1`
- `utils.file.instance_1`
- `tools.tool.instance_1`

**Example Log Output:**

```
2024-01-15 10:30:45,123 - scripts.base.instance_1 - INFO - Initialized scripts.base class
2024-01-15 10:30:45,124 - utils.api.instance_1 - INFO - Initialized API utility
2024-01-15 10:30:45,125 - utils.file.instance_1 - INFO - Initialized File utility
2024-01-15 10:30:45,125 - utils.db.instance_1 - INFO - Initialized DB utility
2024-01-15 10:30:45,126 - scripts.child.instance_1 - INFO - Initialized scripts.child class
2024-01-15 10:30:45,127 - scripts.child.instance_1 - INFO - Starting ETL workflow
2024-01-15 10:30:46,456 - utils.db.instance_1 - INFO - Read 1,250 rows from database.sales.transactions
2024-01-15 10:30:47,789 - scripts.child.instance_1 - INFO - Transformed data: 1,250 → 890 rows
2024-01-15 10:30:48,012 - utils.db.instance_1 - INFO - Upsert completed: 45 inserted, 123 updated
2024-01-15 10:30:48,128 - scripts.child.instance_1 - INFO - ETL workflow completed
2024-01-15 10:30:48,129 - scripts.base.instance_1 - INFO - Disposing of base class
```

### Critical Rules

1. **Always Provide File Paths**
   - All Base/Child classes require explicit log file paths
   - Paths are relative to `logs/` directory
   - Use subdirectories for organization (e.g., `'child/process_1.log'`)

2. **Update base_modules List**
   - When adding new utility classes, add to `base_modules` list in `base.py`
   - When renaming script files, update the list
   - Required in both `configure_logging()` and `dispose()` methods

3. **Log Meaningful Metrics**
   - Always include row counts, processing times, aggregate information
   - Use before/after counts (e.g., "Filtered data: 1,250 → 890 rows")
   - Log at INFO level for normal operations, WARNING for issues

4. **Call dispose() Always**
   - Required for proper file handler cleanup
   - Prevents file locks and memory leaks
   - Call even if errors occur (use try-finally if needed)

## Code Standards

### Type Hints

All method signatures must include type annotations:

```python
def process_data(self, data: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    pass

def get_config(self) -> Dict[str, Any]:
    pass

def read_file(self, path: str) -> Optional[pd.DataFrame]:
    pass
```

### Docstring Format

Use NumPy-style docstrings. Only include sections that are relevant:

```python
def process_data(self, data: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    """
    Process and filter data based on threshold criteria.

    Parameters
    ----------
    data : pd.DataFrame
        Input dataframe to process
    threshold : float, default 0.5
        Minimum threshold for filtering

    Returns
    -------
    pd.DataFrame
        Processed dataframe with applied filters

    Raises
    ------
    ValueError
        If threshold is not between 0 and 1
    """
```

**Rules:**
- Short description on first line
- Blank line before Parameters section
- Include Parameters only if method has parameters
- Include Returns only if method returns something
- Include Raises only if method explicitly raises exceptions
- Use proper type formatting (e.g., `pd.DataFrame`, `Dict[str, Any]`)

### Error Handling

Wrap all methods in try-except blocks:

```python
def extract(self):
    """Extract data from source systems."""
    try:
        # Validate inputs
        if df.empty:
            self.logger.warning("Received empty dataframe")
            return pd.DataFrame()

        if not 0 <= threshold <= 1:
            raise ValueError(f"Threshold must be between 0 and 1, got {threshold}")

        # Process data
        self.logger.info("Starting data extraction")
        # Implementation here

    except Exception as e:
        self.logger.error(f"Data extraction failed: {e}")
        raise  # Re-raise after logging
```

**Rules:**
- Check for empty DataFrames at method start
- Validate parameters before processing
- Log errors with context before re-raising
- Use specific exception types when possible

### Method Organization

Use comment markers to organize code:

```python
class Child(Base):
    # MARK: Initialization
    def __init__(self, file_path: str):
        pass

    # MARK: Wrappers
    def read_data(self, table: str):
        return self.db.read(...)

    # MARK: Business Logic
    def extract(self):
        pass

    def transform(self):
        pass

    # MARK: ETL Methods
    def main(self):
        pass
```

**Common Sections:**
- `# MARK: Initialization` - Constructor and setup
- `# MARK: Wrappers` - Utility wrapper methods
- `# MARK: Business Logic` - Core processing methods
- `# MARK: ETL Methods` - Abstract method implementations
- `# MARK: Helper Methods` - Private/support methods

### Code Grouping

Use strategic whitespace to group related code blocks:

```python
def transform(self):
    """Transform extracted data."""
    try:
        # Validate input
        if self.raw_data.empty:
            self.logger.warning("No data to transform")
            return pd.DataFrame()

        # Apply transformations
        df = self.raw_data.copy()
        df['amount'] = df['amount'].astype(float)
        df['date'] = pd.to_datetime(df['date'])

        # Filter invalid records
        df = df[df['amount'] > 0]
        df = df.dropna(subset=['customer_id'])

        # Log metrics
        self.logger.info(f"Transformed data: {len(self.raw_data)} → {len(df)} rows")
        return df

    except Exception as e:
        self.logger.error(f"Data transformation failed: {e}")
        raise
```

**Rules:**
- Group related operations with blank lines
- Avoid excessive newlines (no more than 1 blank line)
- Use comments to label distinct sections
- Keep logical operations together

## Starting a New Project

### Step 1: Clone Template

```bash
# Clone or download the template
git clone <repository-url>
cd OOB-Python-Project-Template
```

### Step 2: Set Up Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

```bash
# Copy template to .env
cp .env.example .env

# Edit .env with your configuration
# - Database connection strings
# - API keys and tokens
# - File paths
# - Application settings
```

**Key Variables:**
- `SQL_DATABASE_CONN` - Database connection string
- `API_BASE_URL` - Base URL for API calls
- `API_KEY` - API authentication key
- `INPUT_PATH`, `OUTPUT_PATH`, `ARCHIVE_PATH` - File locations

### Step 4: Customize Child Class

Edit `scripts/child.py` to implement your business logic:

```python
class Child(Base):
    def extract(self):
        """Extract data from source systems."""
        try:
            self.logger.info("Starting data extraction")

            # Example: Read from database
            self.raw_data = self.read(
                engine_name="database",
                schema="sales",
                table="transactions",
                table_columns=["id", "amount", "date", "customer_id"],
                where_clause="date >= '2024-01-01'",
                query=None
            )

            self.logger.info(f"Extracted {len(self.raw_data)} rows")

        except Exception as e:
            self.logger.error(f"Data extraction failed: {e}")
            raise

    def transform(self):
        """Transform extracted data."""
        try:
            self.logger.info("Starting data transformation")

            # Your transformation logic here
            self.processed_data = self.raw_data.copy()
            # Apply transformations...

            self.logger.info(f"Transformed: {len(self.raw_data)} → {len(self.processed_data)} rows")

        except Exception as e:
            self.logger.error(f"Data transformation failed: {e}")
            raise

    def load(self):
        """Load transformed data to destination systems."""
        try:
            self.logger.info("Starting data loading")

            # Example: Upsert to database
            result = self.db.upsert(
                df=self.processed_data,
                engine_name="database",
                schema="analytics",
                table="processed_transactions",
                on_condition="target.id = source.id",
                table_columns=["id", "amount", "date", "customer_id"]
            )

            self.logger.info(f"Loaded data: {result['inserted']} inserted, {result['updated']} updated")

        except Exception as e:
            self.logger.error(f"Data loading failed: {e}")
            raise

    def main(self) -> Dict[str, Any]:
        """Main ETL orchestration method."""
        try:
            self.logger.info("Starting ETL workflow")

            # Execute ETL steps
            self.extract()
            self.transform()
            self.load()

            result = {
                'status': 'success',
                'rows_processed': len(self.processed_data)
            }

            self.logger.info("ETL workflow completed")
            return result

        except Exception as e:
            self.logger.error(f"ETL workflow failed: {e}")
            raise
```

### Step 5: Update Database Configuration

Edit `utils/db.py` to add your database connections:

```python
self._dsn_map = {
    "database": os.getenv("SQL_DATABASE_CONN"),
    "warehouse": os.getenv("SQL_WAREHOUSE_CONN"),
    "analytics": os.getenv("SQL_ANALYTICS_CONN"),
}
```

### Step 6: Test Your Implementation

```bash
# Run the main script
python main/main.py

# Or use the batch file
main/main.bat

# Run tests
pytest
pytest --cov=scripts  # With coverage
```

## Common Tasks

### Adding a New Child Class

1. Create new file in `scripts/` directory (e.g., `scripts/reports.py`)
2. Inherit from `Base` class
3. Implement all abstract methods
4. Add to `base_modules` list in `scripts/base.py`:

```python
base_modules = [
    'scripts.base',
    'scripts.child',
    'scripts.reports',  # New class
    'utils.api',
    'utils.file',
    'utils.db',
    'tools.tool'
]
```

5. Create entry point in `main/` if needed

### Adding a New Utility Class

1. Create new file in `utils/` directory (e.g., `utils/email.py`)
2. Implement instance-specific logging pattern:

```python
class Email:
    def __init__(self, instance_id=None):
        if instance_id:
            logger_name = f"utils.email.instance_{instance_id}"
        else:
            logger_name = "utils.email"
        self.logger = logging.getLogger(logger_name)

        self.logger.info("Email utility initialized")
```

3. Initialize in `Base.__init__()`:

```python
self.email = Email(instance_id=self.instance_id)
```

4. Add to `base_modules` list in `scripts/base.py`:

```python
base_modules = [
    'scripts.base',
    'scripts.child',
    'utils.api',
    'utils.file',
    'utils.db',
    'utils.email',  # New utility
    'tools.tool'
]
```

### Creating Configuration Files

Add JSON configuration in `config/` directory:

```json
{
    "column_mappings": {
        "source_column": "target_column",
        "old_name": "new_name"
    },
    "data_types": {
        "id": "int64",
        "amount": "float64",
        "date": "datetime64[ns]"
    },
    "validation_rules": {
        "required_columns": ["id", "amount"],
        "numeric_columns": ["amount", "quantity"],
        "max_null_percentage": 0.05
    }
}
```

Load in your script:

```python
import json

with open('config/mappings.json', 'r') as f:
    config = json.load(f)
```

### Adding Tests

Create test file in `tests/` directory:

```python
import pytest
from scripts.child import Child

class TestChild:
    @pytest.fixture
    def child_instance(self):
        """Create Child instance for testing."""
        child = Child('test/test.log')
        yield child
        child.dispose()

    def test_extract(self, child_instance):
        """Test data extraction."""
        child_instance.extract()
        assert hasattr(child_instance, 'raw_data')
        assert not child_instance.raw_data.empty
```

Run tests:

```bash
pytest tests/test_child.py -v
pytest --cov=scripts --cov-report=html
```

### Adding Dependencies

When adding new Python packages:

```bash
# Install package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt
```

## Project Configuration

### Environment Variables (`.env`)

```env
# Database Connections
SQL_DATABASE_CONN=mssql+pyodbc://server/database?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes

# API Configuration
API_BASE_URL=https://api.example.com/v1
API_KEY=your_api_key_here
API_TIMEOUT=30

# File Paths
INPUT_PATH=./data/input
OUTPUT_PATH=./data/output
ARCHIVE_PATH=./data/archive

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Git Ignore (`.gitignore`)

The template ignores:
- Virtual environments (`venv/`)
- Environment files (`.env`)
- Log files (`*.log`)
- Data files (`*.csv`, `*.xlsx`, `*.json`)
- Python cache (`__pycache__/`)

**Exception:** Files in `config/` and `docs/` are NOT ignored.

### Batch Files

**`main/main.bat`** - Automated execution with environment setup:
```batch
@echo off
call venv\Scripts\activate
git pull
pip install -r requirements.txt
python main/main.py
pause
```

**`main/tool.bat`** - GUI tool launcher:
```batch
@echo off
call venv\Scripts\activate
git pull
pip install -r requirements.txt
python main/tool.py
pause
```

## Best Practices

### Logging

1. **Log Meaningful Metrics**
   ```python
   self.logger.info(f"Read {len(df)} rows from {schema}.{table}")
   self.logger.info(f"Transformed data: {len(input_df)} → {len(output_df)} rows")
   self.logger.info(f"Upsert completed: {inserted} inserted, {updated} updated")
   ```

2. **Use Appropriate Log Levels**
   - `INFO` - Normal operations, metrics, progress
   - `WARNING` - Empty results, skipped operations, non-critical issues
   - `ERROR` - Failures, exceptions, critical problems

3. **Include Context in Error Messages**
   ```python
   except ValueError as e:
       self.logger.error(f"Invalid threshold value: {e}")
       raise
   ```

### Error Handling

1. **Validate Inputs Early**
   ```python
   if df.empty:
       self.logger.warning("Received empty dataframe")
       return pd.DataFrame()

   if not 0 <= threshold <= 1:
       raise ValueError(f"Threshold must be between 0 and 1, got {threshold}")
   ```

2. **Log Before Re-raising**
   ```python
   except Exception as e:
       self.logger.error(f"Data extraction failed: {e}")
       raise  # Re-raise after logging
   ```

3. **Use Specific Exceptions**
   ```python
   if not config_file.exists():
       raise FileNotFoundError(f"Configuration file not found: {config_file}")
   ```

### Resource Management

1. **Always Call dispose()**
   ```python
   child = Child('child/process.log')
   try:
       child.main()
   finally:
       child.dispose()  # Cleanup even if error occurs
   ```

2. **Use Context Managers for Database Connections**
   ```python
   with self.get_engine(engine_name).begin() as conn:
       result = conn.execute(text(query))
   ```

### Code Organization

1. **High-Level Structure**
   - Organize code into well-defined methods (extract, transform, load)
   - Keep methods focused on single responsibility
   - Use clear, descriptive method names

2. **Method Grouping**
   - Use `# MARK:` comments to organize sections
   - Group related methods together
   - Order: Initialization → Wrappers → Business Logic → ETL Methods

3. **Strategic Whitespace**
   - Group related operations with blank lines
   - Avoid excessive newlines
   - Keep logical operations together

## Troubleshooting

### Common Issues

**Issue: Multiple instances logging to same file**
- Ensure each instance gets unique log file path
- Check that `instance_id` is incrementing properly

**Issue: Logger not showing output**
- Verify module name in `base_modules` list
- Check that `configure_logging()` was called
- Ensure logger name follows pattern: `module.instance_{id}`

**Issue: File handler not closing**
- Always call `dispose()` method
- Check that handler is in `base_modules` list
- Verify `dispose()` removes handlers properly

**Issue: Database connection errors**
- Check `.env` file has correct connection string
- Verify database alias in `_dsn_map` dictionary
- Test connection string separately

**Issue: Import errors**
- Verify virtual environment is activated
- Check all dependencies in `requirements.txt`
- Run `pip install -r requirements.txt`

### Debugging Tips

1. **Check Log Files**
   - Logs are in `logs/` directory
   - Organized by module and instance
   - Review for ERROR and WARNING messages

2. **Test Components Independently**
   - Test utility classes separately
   - Verify database connections
   - Check API endpoints

3. **Use Pytest for Validation**
   ```bash
   pytest tests/ -v  # Verbose output
   pytest --pdb      # Drop into debugger on failure
   ```

## Testing with VSCode Pytest Extension

This template is fully configured to work with the VSCode pytest extension for test discovery and execution.

### Test Structure

The testing framework includes:
- **`pytest.ini`** - Pytest configuration at project root
- **`tests/__init__.py`** - Makes tests directory a Python package
- **`tests/conftest.py`** - Shared fixtures and test utilities
- **`tests/test_child.py`** - Tests for Child class
- **`tests/test_db_utils.py`** - Tests for DB utility class
- **`.vscode/settings.json`** - VSCode pytest extension configuration

### Required Package Structure

**CRITICAL:** All directories must have `__init__.py` files for imports to work:
```
scripts/__init__.py
utils/__init__.py
tools/__init__.py
tests/__init__.py
main/__init__.py
config/__init__.py
```

Without these files, pytest and VSCode will not be able to import modules correctly.

### Pytest Configuration

The [pytest.ini](pytest.ini) file configures:
- **pythonpath = .** - Adds project root to Python path (fixes import errors)
- **testpaths = tests** - Test discovery in tests directory
- **Markers** - Categorize tests (unit, integration, slow, db, api)
- **Default options** - Verbose output, short tracebacks

### VSCode Settings

The [.vscode/settings.json](.vscode/settings.json) configures:
- Pytest as the test framework
- Test discovery in `tests/` directory
- Auto-discovery on save
- Pylance language server with project root in extra paths

### Running Tests

**In VSCode:**
1. Open the Testing view (beaker icon in sidebar)
2. Tests will be automatically discovered
3. Click the play button next to any test to run it
4. View results in the Test Explorer

**Command Line:**
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_child.py

# Run specific test class
pytest tests/test_child.py::TestChildInitialization

# Run specific test
pytest tests/test_child.py::TestChildInitialization::test_child_initialization

# Run with coverage
pytest --cov=scripts --cov=utils

# Run only unit tests (using markers)
pytest -m unit

# Run only integration tests
pytest -m integration
```

### Test Fixtures

**Common Fixtures in conftest.py:**

1. **sample_dataframe** - Creates test DataFrame with sample data
2. **empty_dataframe** - Creates empty DataFrame for edge cases
3. **temp_directory** - Creates temporary directory, cleans up after test
4. **child_instance** - Creates Child class instance, calls dispose() after test
5. **db_instance** - Creates DB utility instance with instance_id=1
6. **api_instance** - Creates API utility instance
7. **file_instance** - Creates File utility with temp directories
8. **sample_csv_file** - Creates sample CSV file in temp directory
9. **sample_excel_file** - Creates sample Excel file
10. **setup_test_environment** - Auto-use fixture that sets test env vars

### Writing New Tests

**Pattern for testing classes with fixtures:**

```python
class TestYourClass:
    """Test suite for YourClass."""

    def test_initialization(self, child_instance):
        """Test class initializes correctly."""
        assert child_instance is not None
        assert hasattr(child_instance, 'logger')

    def test_method_with_mock(self, child_instance):
        """Test method with mocked dependencies."""
        child_instance.db.read = Mock(return_value=pd.DataFrame({'id': [1]}))

        result = child_instance.db.read(
            engine_name='test',
            schema='test',
            table='test',
            table_columns=['id'],
            where_clause=None,
            query=None
        )

        assert isinstance(result, pd.DataFrame)
```

**Pattern for resource cleanup:**

```python
@pytest.fixture
def your_fixture():
    """Create resource for testing."""
    resource = YourClass('test/test.log')
    yield resource
    resource.dispose()  # Cleanup after test
```

### Test Markers

Use markers to categorize tests:

```python
@pytest.mark.unit
def test_basic_functionality():
    """Unit test."""
    pass

@pytest.mark.integration
def test_with_database():
    """Integration test requiring database."""
    pass

@pytest.mark.slow
def test_long_running():
    """Test that takes time to run."""
    pass

@pytest.mark.db
def test_database_operation():
    """Test requiring database connection."""
    pass
```

Run specific categories:
```bash
pytest -m unit        # Run only unit tests
pytest -m "not slow"  # Skip slow tests
pytest -m "db or api" # Run database or API tests
```

### Troubleshooting Test Issues

**Issue: Import errors in tests**
- Solution: Ensure all directories have `__init__.py` files
- Verify `pytest.ini` has `pythonpath = .`
- Check VSCode settings has `"python.analysis.extraPaths": ["."]`

**Issue: Tests not discovered in VSCode**
- Solution: Reload VSCode window (Ctrl+Shift+P → "Reload Window")
- Check `.vscode/settings.json` has `"python.testing.pytestEnabled": true`
- Verify test files follow naming pattern `test_*.py`

**Issue: Fixture not found errors**
- Solution: Ensure `conftest.py` is in `tests/` directory
- Check fixture function names match parameters in tests
- Verify `tests/__init__.py` exists

**Issue: Module import errors during test execution**
- Solution: Activate virtual environment in VSCode
- Install all dependencies: `pip install -r requirements.txt`
- Ensure project root is in Python path

**Issue: Log files created during tests**
- Expected: Tests create log files in `logs/test/` directory
- Solution: This is normal behavior; logs help debug test failures
- Add `logs/test/` to `.gitignore` if needed

### Example Test Output

```bash
$ pytest tests/test_child.py -v

tests/test_child.py::TestChildInitialization::test_child_initialization PASSED
tests/test_child.py::TestChildInitialization::test_child_has_base_methods PASSED
tests/test_child.py::TestChildETLMethods::test_extract_method_exists PASSED
tests/test_child.py::TestChildETLMethods::test_main_method_returns_dict PASSED
tests/test_child.py::TestChildLogging::test_logger_has_correct_name PASSED

===================== 5 passed in 0.45s =====================
```

## Version Information

**Template Version:** 1.0

**Python Version:** 3.8+ (avoid 3.13+ for compatibility with data libraries)

**Key Dependencies:**
- pandas >= 1.5.0
- sqlalchemy >= 2.0.0
- requests >= 2.28.0
- python-dotenv >= 0.19.0
- pytest >= 7.0.0

## Summary Checklist

When starting a new project with this template:

- [ ] Clone template repository
- [ ] Create and activate virtual environment
- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Copy `.env.example` to `.env` and configure
- [ ] Update `_dsn_map` in `utils/db.py` with your databases
- [ ] Implement `extract()`, `transform()`, `load()`, `main()` in `scripts/child.py`
- [ ] If adding utilities, update `base_modules` list in `scripts/base.py`
- [ ] Create tests in `tests/` directory
- [ ] Add configuration files to `config/` if needed
- [ ] Document database schema in `docs/schema.sql`
- [ ] Test with `python main/main.py`
- [ ] Run tests with `pytest`
- [ ] Update `requirements.txt` if adding dependencies

---

**This guide provides Claude with comprehensive context about the project structure, patterns, and conventions to effectively work with this Python OOB template.**
