# Testing Guide

This document describes the testing strategies and approaches used in the MoneyMoney Python library.

## Overview

The test suite is designed to handle the external dependency of a running MoneyMoney application through a combination of unit tests with mocked data and optional integration tests against the real application.

## Test Structure

### Unit Tests (`tests/test_accounts.py`)
- **Purpose**: Test core functionality using mocked data
- **Dependencies**: None (uses `MockedBackend`)
- **Data Source**: `tests/backend_config.yml`
- **Execution**: Always run in CI/CD

### Integration Tests (`tests/test_integration.py`)
- **Purpose**: Test against real MoneyMoney application
- **Dependencies**: MoneyMoney.app installed and running
- **Execution**: Only run when MoneyMoney is available
- **Markers**: `@pytest.mark.integration`

### Test Utilities (`tests/test_utilities.py`)
- **Purpose**: Provide utilities for creating mock data and test scenarios
- **Components**:
  - `MockDataBuilder`: Build comprehensive test datasets
  - `MockBackendFactory`: Create mock backends with different configurations
  - Data classes for transactions, accounts, positions, and categories

## External Dependency Handling

### Strategy 1: Mocking (Primary)
The primary testing strategy uses a `MockedBackend` class that implements the `BackendInterface` but uses static test data instead of communicating with the real MoneyMoney application.

**Advantages:**
- Fast execution
- Deterministic results
- No external dependencies
- Works in CI/CD environments
- Can test edge cases easily

**Implementation:**
```python
class MockedBackend(BackendInterface):
    def __init__(self, data):
        self.data = data
    
    def get_accounts(self):
        return self.data["accounts"]
    # ... other methods
```

### Strategy 2: Integration Testing (Optional)
Integration tests can optionally run against the real MoneyMoney application when it's available.

**Advantages:**
- Tests real-world scenarios
- Validates actual MoneyMoney integration
- Catches integration-specific issues

**Implementation:**
```python
@pytest.mark.integration
@pytest.mark.skipif(
    not os.path.exists("/Applications/MoneyMoney.app"),
    reason="MoneyMoney application not found"
)
class TestMoneyMoneyIntegration:
    # ... integration tests
```

### Strategy 3: Test Data Management
Comprehensive test data is managed through YAML files and programmatic builders.

**Test Data Sources:**
1. `tests/backend_config.yml` - Static test data
2. `MockDataBuilder` - Programmatic test data creation
3. `create_test_scenarios()` - Predefined test scenarios

## Running Tests

### Unit Tests Only (Default)
```bash
pipenv run pytest tests/ -m "not integration"
```

### Integration Tests Only
```bash
pipenv run pytest tests/ -m "integration"
```

### All Tests
```bash
pipenv run pytest tests/
```

### With Coverage
```bash
pipenv run pytest tests/ --cov=money --cov-report=html
```

## Test Data Management

### Static Test Data
The `tests/backend_config.yml` file contains comprehensive test data including:
- Multiple accounts (bank accounts and portfolios)
- Various transaction types with different properties
- Portfolio positions with profit/loss calculations
- Category hierarchies
- Realistic financial data

### Dynamic Test Data
The `MockDataBuilder` class allows programmatic creation of test data:

```python
builder = MockDataBuilder()
builder.add_account(MockAccountData("Test Bank", "TB001", 1000.00))
builder.add_transaction("TB001", MockTransactionData(
    id="tx001",
    account_number="TB001",
    amount=100.00,
    name="Test Transaction"
))
mock_backend = MockBackendFactory.create_from_builder(builder)
```

### Test Scenarios
Predefined test scenarios are available:
- `empty`: No data
- `single_account`: One account only
- `high_volume`: Many transactions
- `complex_portfolio`: Multiple positions

## CI/CD Integration

### GitHub Actions
The project includes a comprehensive GitHub Actions workflow that:
- Runs on multiple Python versions (3.9-3.12)
- Tests on both Ubuntu and macOS
- Runs unit tests on all platforms
- Runs integration tests only on macOS (where MoneyMoney is available)
- Includes linting and code coverage reporting

### Test Markers
Tests are organized using pytest markers:
- `@pytest.mark.unit`: Unit tests (default)
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.slow`: Slow-running tests
- `@pytest.mark.external`: Tests requiring external dependencies

## Best Practices

### Writing Unit Tests
1. Use descriptive test names
2. Test one concept per test
3. Use parametrized tests for similar scenarios
4. Include both positive and negative test cases
5. Test edge cases and error conditions

### Writing Integration Tests
1. Mark with `@pytest.mark.integration`
2. Skip if external dependency is not available
3. Don't assume specific data exists
4. Clean up any changes made during testing
5. Use realistic test data

### Mock Data Creation
1. Use the `MockDataBuilder` for complex scenarios
2. Create reusable test data factories
3. Include realistic financial data
4. Test various data combinations
5. Document test data assumptions

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the package is installed in development mode:
   ```bash
   pipenv run pip install -e .
   ```

2. **Missing Dependencies**: Install development dependencies:
   ```bash
   pipenv install --dev
   ```

3. **Integration Test Failures**: Check if MoneyMoney is installed and running:
   ```bash
   ls -la /Applications/MoneyMoney.app
   ```

4. **Coverage Issues**: Ensure all code paths are tested and coverage thresholds are met.

### Debug Mode
Run tests with verbose output and debugging:
```bash
pipenv run pytest tests/ -v -s --tb=long
```

## Future Enhancements

1. **Property-based Testing**: Use Hypothesis for property-based testing
2. **Performance Testing**: Add benchmarks for large datasets
3. **Contract Testing**: Test against MoneyMoney API contracts
4. **Visual Testing**: Add visual regression testing for data exports
5. **Load Testing**: Test with large datasets and high transaction volumes