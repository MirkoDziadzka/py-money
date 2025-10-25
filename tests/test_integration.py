"""
Integration tests for MoneyMoney backend.

These tests can optionally run against a real MoneyMoney application.
They are marked with pytest markers to allow selective execution.
"""

import os
from datetime import date, timedelta

import pytest
import yaml

from money import MoneyMoney
from money.backends.MoneyMoney import Backend


@pytest.mark.integration
@pytest.mark.skipif(
    not os.path.exists("/Applications/MoneyMoney.app"),
    reason="MoneyMoney application not found"
)
class TestMoneyMoneyIntegration:
    """Integration tests that require a running MoneyMoney application."""

    @pytest.fixture
    def real_backend(self):
        """Create a real MoneyMoney backend for integration testing."""
        return Backend()

    @pytest.fixture
    def real_instance(self, real_backend):
        """Create a MoneyMoney instance with real backend."""
        try:
            return MoneyMoney(backend=real_backend)
        except (ConnectionError, RuntimeError, OSError) as e:
            if "Locked database" in str(e):
                pytest.skip(
                    "MoneyMoney database is locked - please unlock it to run integration tests")
            else:
                pytest.skip(f"MoneyMoney integration test skipped: {e}")
        except Exception as e:  # pylint: disable=broad-except
            pytest.skip(f"MoneyMoney integration test skipped: {e}")
        # This line should never be reached, but satisfies pylint
        return None

    def test_real_accounts_exist(self, real_instance):
        """Test that we can retrieve real accounts from MoneyMoney."""
        accounts = list(real_instance.accounts())
        assert len(accounts) > 0, "No accounts found in MoneyMoney"

        # Check that accounts have required attributes
        for account in accounts:
            assert hasattr(account, 'name')
            assert hasattr(account, 'account_number')
            assert hasattr(account, 'balance')
            assert hasattr(account, 'currency')

    def test_real_portfolios_exist(self, real_instance):
        """Test that we can retrieve real portfolios from MoneyMoney."""
        portfolios = list(real_instance.portfolios())
        # Note: This test might pass even if no portfolios exist
        # as portfolios are optional

        # Check that portfolios have required attributes
        for portfolio in portfolios:
            assert hasattr(portfolio, 'name')
            assert hasattr(portfolio, 'account_number')
            assert portfolio.is_portfolio is True

    def test_real_transactions_exist(self, real_instance):
        """Test that we can retrieve real transactions from MoneyMoney."""
        # Get a recent date range
        end_date = date.today()
        start_date = end_date - timedelta(days=30)

        for account in real_instance.accounts():
            transactions = list(account.transactions(
                start_date=start_date,
                end_date=end_date
            ))
            if transactions:
                # Check that transactions have required attributes
                for tx in transactions:
                    assert hasattr(tx, 'id')
                    assert hasattr(tx, 'amount')
                    assert hasattr(tx, 'currency')
                    assert hasattr(tx, 'name')
                break

        # This test might pass even if no recent transactions exist
        # as it depends on the user's actual data

    def test_real_categories_exist(self, real_instance):
        """Test that we can retrieve real categories from MoneyMoney."""
        categories = list(real_instance.categories())
        # Categories might be empty if none are defined
        # but the method should not raise an exception

        # Check that categories have required attributes
        for category in categories:
            assert hasattr(category, 'name')
            assert hasattr(category, 'id')

    def test_real_positions_exist(self, real_instance):
        """Test that we can retrieve real portfolio positions from MoneyMoney."""
        for portfolio in real_instance.portfolios():
            positions = list(portfolio.positions())
            if positions:
                # Check that positions have required attributes
                for pos in positions:
                    assert hasattr(pos, 'name')
                    assert hasattr(pos, 'quantity')
                    assert hasattr(pos, 'price')
                break

        # This test might pass even if no positions exist
        # as it depends on the user's actual portfolio data


@pytest.mark.integration
@pytest.mark.skipif(
    os.path.exists("/Applications/MoneyMoney.app"),
    reason="MoneyMoney application is running - skipping mock tests"
)
class TestMoneyMoneyMockedIntegration:
    """Integration tests that run when MoneyMoney is not available."""

    def test_mocked_backend_fallback(self):
        """Test that the system gracefully handles missing MoneyMoney app."""
        # This test verifies that our mocking system works
        # when the real MoneyMoney app is not available
        from tests.conftest import MockedBackend

        # Load test data
        test_data_path = os.path.join(
            os.path.dirname(__file__), "backend_config.yml")
        with open(test_data_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        backend = MockedBackend(data)
        instance = MoneyMoney(backend=backend)

        # Verify that mocked data works
        accounts = list(instance.accounts())
        assert len(accounts) > 0

        categories = list(instance.categories())
        assert len(categories) > 0

    def test_mocked_data_consistency(self):
        """Test that mocked data is consistent and valid."""
        from tests.conftest import MockedBackend
        # Load test data
        test_data_path = os.path.join(
            os.path.dirname(__file__), "backend_config.yml")
        with open(test_data_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        backend = MockedBackend(data)
        instance = MoneyMoney(backend=backend)

        # Test data consistency
        accounts = list(instance.accounts())
        for account in accounts:
            assert hasattr(account, 'name')
            assert hasattr(account, 'account_number')
            assert hasattr(account, 'balance')
