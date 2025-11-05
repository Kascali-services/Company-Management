# Test Suite for Unternehmen Management System

This directory contains comprehensive tests for the German company management system.

## Test Structure

```
tests/
├── conftest.py                           # Shared fixtures and test configuration
├── test_helpers.py                       # Helper functions and factory classes
├── unit/                                 # Unit tests
│   ├── test_models_unternehmen.py       # Unternehmen model tests
│   ├── test_models_person.py            # Person model tests
│   ├── test_schemas_unternehmen.py      # Unternehmen schema validation tests
│   ├── test_schemas_person.py           # Person schema validation tests
│   ├── test_core_config.py              # Configuration tests
│   ├── test_core_database.py            # Database setup tests
│   └── test_utils_constants.py          # Constants tests
└── integration/                          # Integration tests
    ├── test_routes_unternehmen.py       # Unternehmen API endpoint tests
    ├── test_routes_person.py            # Person API endpoint tests
    └── test_routes_export.py            # Export API endpoint tests
```

## Installation

Install test dependencies:

```bash
pip install -r requirements-test.txt
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage report
```bash
pytest --cov=app --cov-report=term-missing --cov-report=html
```

### Run specific test categories
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests for a specific module
pytest tests/unit/test_models_unternehmen.py

# Run a specific test
pytest tests/unit/test_models_unternehmen.py::TestUnternehmenModel::test_create_unternehmen_success
```

### Run with verbose output
```bash
pytest -v
```

### Run tests in parallel (faster)
```bash
pip install pytest-xdist
pytest -n auto
```

## Test Coverage

The test suite aims for high code coverage (90%+) across all modules:

- **Models**: Tests for SQLAlchemy models, relationships, and constraints
- **Schemas**: Pydantic validation testing for all input/output schemas
- **Routes**: Full API endpoint testing including success and error cases
- **Core**: Database and configuration setup tests
- **Utils**: Utility functions and constants tests

### Coverage Report

After running tests with coverage, view the HTML report:

```bash
# Open in browser (Windows)
start htmlcov/index.html

# Open in browser (Linux/Mac)
open htmlcov/index.html
```

## Test Fixtures

Key fixtures available in `conftest.py`:

- `test_db`: Database session for each test
- `client`: FastAPI TestClient with database override
- `create_unternehmen`: Factory for creating test companies
- `create_person`: Factory for creating test persons
- `sample_unternehmen_data`: Sample company data dictionary
- `sample_person_data`: Sample person data dictionary
- `unternehmen_with_persons`: Complete company with Ansprechpartner and Empfehler
- `multiple_unternehmen`: Multiple companies for pagination tests

## Test Helpers

The `test_helpers.py` module provides:

- `UnternehmenFactory`: Factory for generating company test data
- `PersonFactory`: Factory for generating person test data
- `assert_response_status()`: Helper for asserting HTTP status codes
- `assert_validation_error()`: Helper for asserting validation errors
- `assert_unternehmen_equal()`: Helper for comparing company data
- `assert_person_equal()`: Helper for comparing person data

## Key Test Scenarios

### Business Logic Tests

1. **Ansprechpartner Constraint**: Company can have only ONE Ansprechpartner
2. **Multiple Empfehler**: Company can have MULTIPLE Empfehler
3. **Circular Relationship**: Tests for Unternehmen ↔ Person relationships
4. **Cascade Deletion**: Tests for deletion behavior

### Validation Tests

1. **PLZ Validation**: Must be exactly 5 digits
2. **Bundesland Validation**: Must be one of 16 German states
3. **Rolle Validation**: Must be "Empfehler" or "Ansprechpartner"
4. **Funktion Validation**: Must be "Mitarbeiter" or "Azubi"

### API Tests

1. **CRUD Operations**: Create, Read, Update, Delete for all entities
2. **Pagination**: Skip and limit parameters
3. **Search**: Full-text search across multiple fields
4. **Sorting**: Sort by name, bundesland, stadt, plz
5. **Export**: CSV and Excel export functionality

## Test Database

Tests use SQLite in-memory database for:
- Fast execution
- Isolation between tests
- No need for external database setup

## Continuous Integration

To integrate with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements-test.txt
    pytest --cov=app --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Troubleshooting

### Import errors
If you get import errors, ensure you're running from the project root:
```bash
cd C:/Git/Business/Unterbehmen_management
pytest
```

### Database errors
Tests use SQLite in-memory, so no PostgreSQL needed. If you get database errors, check that SQLAlchemy models are imported correctly.

### Fixture not found
Make sure `conftest.py` is in the `tests/` directory and pytest can discover it.

## Writing New Tests

When adding new tests, follow the AAA pattern:

```python
def test_example(fixture_name):
    """
    Brief description of what this test does.

    Arrange: Setup test data and preconditions
    Act: Execute the code being tested
    Assert: Verify expected outcomes
    """
    # Arrange
    data = create_test_data()

    # Act
    result = function_under_test(data)

    # Assert
    assert result == expected_value
```

## Test Markers

Available pytest markers:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.slow`: Slow-running tests

Use markers to selectively run tests:
```bash
pytest -m "not slow"  # Skip slow tests
```
