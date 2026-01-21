# Python Automation/Tools Project Template

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)

A comprehensive object-oriented Python project template designed for ETL (Extract, Transform, Load) processes, API integrations, software tools or automation workflows. This template provides a structured foundation for building scalable data processing applications with proper logging, error handling, and modular design patterns.

## 🏗️ Project Overview

This template is designed for general software or backend projects that involve:
- **Database Operations**: Reading from and writing to various databases
- **API Integrations**: Consuming and processing data from REST APIs
- **File Processing**: Handling CSV, Excel, and text files
- **Data Transformation**: ETL pipelines with pandas and other data tools
- **GUI Tools**: Tkinter-based interfaces for manual operations
- **Automation**: Scheduled processes and batch operations

### Architecture

```
📁 Project Root
├── 📁 main/           # Entry points and batch files
├── 📁 scripts/        # Core classes (Base & Child)
├── 📁 utils/          # Utility classes (DB, API, File operations)
├── 📁 tools/          # GUI tools and manual operation interfaces
├── 📁 tests/          # Unit tests and test utilities
├── 📁 config/         # Configuration files and mappings
├── 📁 docs/           # Documentation, schemas, and references
└── 📁 logs/           # Application logs (organized by module)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher (Note: Python 3.13+ may have compatibility issues with some data libraries)
- Virtual environment (recommended)
- Windows (recommended), otherwise switch out bat files with suitable alternative

### Installation

1. **Clone or download this template**
2. **Set up virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.template .env
   # Edit .env with specific configuration
   ```

5. **Run the example:**
   ```bash
   python -m main/main.py
   # or use the batch file
   main/main.bat
   ```

## ⚙️ Setup & Configuration

### Environment Variables

A `.env` file can be created in the project root to store secrets, tokens logins etc, such as the example below:

```env
# Database Connections
SQL_DATABASE_CONN=mssql+pyodbc://server/database?driver=ODBC+Driver+17+for+SQL+Server

# API Configuration
API_BASE_URL=https://api.example.com
API_KEY=api_key
API_TIMEOUT=30

# File Paths
INPUT_PATH=./data/input
OUTPUT_PATH=./data/output
ARCHIVE_PATH=./data/archive
```

### Dependencies
When adding new dependencies to the project, update the requirements.txt file to maintain consistency across development environments.

**Replace requirements.txt with installed dependencies:**
```batch
pip freeze > requirements.txt
```
#### Commonly Required Dependencies
- `pandas` - Data manipulation and analysis
- `requests` - HTTP library for API calls
- `sqlalchemy` - Database toolkit and ORM
- `python-dotenv` - Environment variable management
- `pytest` - Testing framework

## 📋 Main Entry Points

The main directory contains the primary execution scripts and batch files for running the scripts.

### `main/main.py`
- Initializes Child class instances with specific log files
- Executes main workflows with proper resource disposal
- Demonstrates multiple instances running with separate logging
- Handles command-line arguments
- Manages process logging and error handling

### `main/main.bat`
- Activates virtual environment
- Updates code from version control
- Installs/updates dependencies
- Executes main process

### `main/tool.bat`
- Activates virtual environment
- Updates code from version control
- Installs/updates dependencies
- Launches GUI or CLI tools for manual operations

## 📝 Logging

This template implements a sophisticated instance-specific logging system that enables multiple script instances to run simultaneously with isolated log files while maintaining clear hierarchical logger naming conventions.

### Configuration
All logging uses this format:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

**Example log output:**
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
2024-01-15 10:30:45,128 - scripts.child.instance_1 - INFO - ETL workflow completed
2024-01-15 10:30:45,129 - scripts.base.instance_1 - INFO - Disposing of base class
```

### Instance-Specific Logging
Instance-specific logging system that ensures multiple objects can run simultaneously with separate log files while maintaining clear logger hierarchies.

- **Unique instances**: Each object gets instance-specific loggers (e.g., `scripts.child.instance_1`, `scripts.child.instance_2`)
- **Separate files**: Multiple instances can run simultaneously with their own log files without cross-contamination
- **Clear hierarchy**: Logger names preserve module structure while adding instance identification
- **Always provide file paths**: All classes require explicit log file paths
- **Module list maintenance**: When adding/removing utility classes or renaming script files, update the `base_modules` list in `scripts/base.py` to ensure proper logger cleanup
- **File management**: Logs overwrite by default; use timestamps in filenames for archival

### Best Practices
- **Include metrics**: Always log row counts, processing times, and aggregate information
- **Proper disposal**: Always call `dispose()` to clean up logging handlers
- **Hierarchical naming**: Use module.class.instance naming (e.g., `utils.db.instance_{n}`, `scripts.child.instance_{n}`)

## 🧩 Scripts

Core classes that implement the main processes and business logic, including the abstract base class and concrete implementations.

### `base.py` - Abstract Base Class
- **Instance-Specific Logging**: Configures standardized logging for each instance
- **Utility Initialization**: Initializes utility objects with instance-specific loggers
- **Utility Wrappers**: Provides wrapper methods for accessing utility objects.
- **Abstract Methods**: Enforces common patterns children must follow (Ex: extract, transform, load, main)
- **Common Functionality**: Provides common methods used across all children (e.g., `dispose()` method for cleanup)
- **Required Parameters**: Optionally include parameters for configurations common among all children (e.g., `file_path: str` - to specify log file location)

### `child.py` - Concrete Implementation
- **Abstract Method Implementation**: Implements required abstract methods from base class (main workflow and any defined process steps)
- **Business Logic Methods**: Contains processing logic and workflows specific to the use case (e.g., financial calculations, inventory management, customer segmentation)
- **Workflow Execution**: Coordinates the complete process pipeline (e.g., extract-transform-load for ETL projects)
- **Instance Configuration**: Accepts child-specific parameters and passes common configurations to base class (e.g., `file_path: str` for log file location)

### Best Practices
- **Method Organization**: Separate methods into logical groups using comments (e.g., `# MARK: Wrappers`, `# MARK: Business Logic`)
- **High-Level Structure**: Organize code into well-defined, high-level functions that follow the workflow pattern (e.g., extract, transform, load methods for ETL projects)
- **Clear Purpose**: Each method should have a clear purpose with concise names

### Coding Standards

#### Key Principles
- **Input validation**: Check for empty DataFrames, null values, and invalid parameters
- **Error handling**: Wrap all methods in try-except blocks with logging and optionally re-raising
- **Comments**: Include concise comments in appropriate locations
- **Code Grouping**: Use strategic whitespace to group related code blocks, avoiding excessive newlines while maintaining readability
- **Documentation**: Complete docstrings following the specified format, only include headers if they are present in the method (e.g., Don't include Parameters if there are no parameters)
- **Type hints**: Include method signatures with proper type annotations

#### Docstring Structure Example
```python
    """
    Short method description.

    Parameters
    ----------
    parameter name : DataType
        Short description

    Returns
    -------
    DataType
        Short description

    Raises
    ------
    ErrorType
        Short description
    """
```

#### Method Structure Example
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
    try:
        # Validate inputs
        if data.empty:
            self.logger.warning("Received empty dataframe")
            return pd.DataFrame()

        if not 0 <= threshold <= 1:
            raise ValueError(f"Threshold must be between 0 and 1, got {threshold}")

        # Process data
        filtered_data = data[data['score'] >= threshold]
        self.logger.info(f"Filtered data: {len(data)} → {len(filtered_data)} rows")

        return filtered_data

    except Exception as e:
        self.logger.error(f"Error processing data: {e}")
        raise
```

## 🔧 Tools

GUI applications and interactive tools for manual operations, data management, and process monitoring. Tools integrate with the instance-specific logging system and provide sensible defaults for log file locations.

### Key Features:
- **Automated Script Integration**: Optional integration to Child class functionality
- **Resource Management**: Proper disposal of resources

Example Tool Usage:

```python
from tools.tool import Tool

# Using default log location (tool/tool.log)
tool = Tool()
tool.run()
tool.dispose()
```

## 🛠️ Utilities

Reusable utility classes for common operations like database access, API interactions, and file processing. See below for common examples of utility classes.

### `db.py` - Database Operations (Template)
- **Connection Management**: Multiple database connections with pooling
- **Pandas Integration**: Direct DataFrame read/write operations
- **Bulk Operations**: Efficient insert/upsert capabilities
- **Error Handling**: Robust exception handling with detailed logging

### `api.py` - API Interactions (Template)
- **Request Handling**: GET, POST, PUT, DELETE operations
- **Authentication**: Bearer token and API key management
- **Retry Logic**: Automatic retry with exponential backoff
- **Rate Limiting**: Request throttling and queue management

### `file.py` - File Processing (Template)
- **Format Support**: CSV, Excel, TXT file handling
- **Data Validation**: Schema validation and data quality checks
- **File Management**: Archive, backup, and cleanup operations
- **Encoding Handling**: UTF-8, ASCII, and other encoding support

## 🧪 Tests

Comprehensive testing framework with pytest fixtures, test utilities, and examples for unit and integration testing.

### Test Structure

```
📁 tests/
├── test_base.py           # Base class tests
├── test_child.py          # Child class tests
├── test_db_utils.py       # Database utility tests
├── conftest.py            # Pytest fixtures
└── data/                  # Test data files
```

### Running Tests
```bash
pytest                     # Run all tests
pytest --cov=scripts       # Run with coverage
pytest tests/test_db_utils.py -v  # Run specific file
```

## 📁 Config

The config directory contains project-specific configuration files and data mappings.

### Purpose
Use this directory for:
- **Data mappings** - Column mappings, data type definitions, validation rules
- **Business rules** - Thresholds, categories, lookup tables
- **Environment configs** - Different settings for dev/staging/production
- **API configurations** - Endpoint mappings, request templates

### Example: `mappings.json`
Template for data transformation and validation configurations:
```json
{
    "column_mappings": {
        "source_column_name": "target_column_name",
        "old_field": "new_field"
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

## 📚 Docs

The docs directory contains project documentation, references, and technical specifications.

### Purpose
Use this directory for:
- **Database schemas** - SQL scripts for table creation, indexes, stored procedures
- **API documentation** - Endpoint specifications, authentication details, examples
- **Data flow diagrams** - Visual representations of processes and system architecture
- **Business requirements** - Functional specifications and business rules documentation
- **External references** - Links to third-party APIs, vendor documentation

### Example Files
- **`schema.sql`** - Database schema definitions and setup scripts for the project's tables
- **`ERD.png`** - Entity Relationship Diagram showing table structures and relationships
- **`api_reference.md`** - Documentation for external APIs used in the project
- **`data_dictionary.xlsx`** - Field definitions, data types, and business meanings

## 🚀 Deployment

### Batch File Automation
The template includes Windows batch files for automated deployment:
- `main/main.bat` - Production automation execution with environment setup
- `main/tool.bat` - GUI tool launcher with environment setup

### CI/CD Integration
**TBD** - This section will be expanded when CI/CD pipelines are implemented. Examples include:
- GitHub Actions or Azure DevOps workflows
- Automated testing and deployment
- Environment-specific configurations
- Containerization with Docker

## 📚 Resources

Links to external documentation and learning resources for commonly used modules.

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Requests Documentation](https://docs.python-requests.org/)
- [Tkinter Tutorial](https://docs.python.org/3/library/tkinter.html)
- [Pytest Documentation](https://docs.pytest.org/)

---

**Template Version**: 1.0
