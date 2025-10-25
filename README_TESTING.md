# Testing Setup for MoneyMoney Python Library

## Overview

This project now includes a comprehensive automated test suite that handles the external dependency of a running MoneyMoney application through multiple strategies:

1. **Unit Tests** - Fast, reliable tests using mocked data
2. **Integration Tests** - Optional tests against real MoneyMoney application
3. **Test Utilities** - Tools for creating mock data and test scenarios

## Quick Start

### Run Unit Tests (Recommended)
```bash
pipenv run pytest tests/ -m "not integration"
```

### Run All Tests
```bash
pipenv run pytest tests/
```

### Run with Coverage
```bash
pipenv run pytest tests/ --cov=money --cov-report=html
```

### Use Test Runner Script
```bash
# Run unit tests
python scripts/run_tests.py --type unit

# Run with coverage
python scripts/run_tests.py --type coverage

# Run linting
python scripts/run_tests.py --lint

# Clean up test artifacts
python scripts/run_tests.py --clean
```

## External Dependency Handling

### Strategy 1: Mocking (Primary)
- Uses `MockedBackend` class with static test data
- No external dependencies required
- Fast execution, deterministic results
- Works in CI/CD environments

### Strategy 2: Integration Testing (Optional)
- Tests against real MoneyMoney application when available
- Automatically skips if MoneyMoney is not installed or database is locked
- Provides real-world validation

### Strategy 3: Test Data Management
- Comprehensive test data in `tests/backend_config.yml`
- Programmatic test data creation with `MockDataBuilder`
- Multiple test scenarios for different use cases

## Test Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_accounts.py         # Unit tests for core functionality
├── test_integration.py      # Integration tests (optional)
├── test_utilities.py        # Test utilities and mock data builders
└── backend_config.yml       # Static test data
```

## CI/CD Integration

- **GitHub Actions** workflow runs on multiple Python versions
- **Unit tests** run on all platforms
- **Integration tests** only run on macOS when MoneyMoney is available
- **Linting** and **coverage** reporting included

## Test Data

The test suite includes realistic financial data:
- Multiple bank accounts and portfolios
- Various transaction types with categories and tags
- Portfolio positions with profit/loss calculations
- Category hierarchies
- Edge cases and error conditions

## Best Practices

1. **Unit tests** are the primary testing strategy
2. **Integration tests** provide additional validation when possible
3. **Mock data** is comprehensive and realistic
4. **Test utilities** make it easy to create new test scenarios
5. **CI/CD** ensures tests run automatically on all changes

## Troubleshooting

### Common Issues

1. **Import Errors**: Run `pipenv run pip install -e .`
2. **Missing Dependencies**: Run `pipenv install --dev`
3. **Integration Test Failures**: MoneyMoney database may be locked
4. **Coverage Issues**: Ensure all code paths are tested

### Debug Mode
```bash
pipenv run pytest tests/ -v -s --tb=long
```

## Future Enhancements

- Property-based testing with Hypothesis
- Performance testing with large datasets
- Contract testing against MoneyMoney API
- Visual regression testing for data exports

## Summary

The test suite successfully handles the external MoneyMoney dependency through:
- ✅ Comprehensive unit testing with mocked data
- ✅ Optional integration testing with graceful fallbacks
- ✅ Robust test data management
- ✅ CI/CD integration with proper platform handling
- ✅ Clear documentation and best practices

This approach ensures reliable, fast testing while still providing the option to validate against the real MoneyMoney application when available.