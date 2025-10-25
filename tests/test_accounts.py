""" unit tests
"""

import pytest

from money import MoneyMoney


def test_accounts_are_present(instance: MoneyMoney):
    accounts = list(instance.accounts())
    assert len(accounts) == 2


@pytest.mark.parametrize("name", ["Postbank", "Deutsche Bank"])
def test_accounts_have_name(instance, name):
    assert name in (a.name for a in instance.accounts())


def test_portfolios_are_present(instance: MoneyMoney):
    portfolios = list(instance.portfolios())
    assert len(portfolios) == 1


@pytest.mark.parametrize("name", ["Comdirect"])
def test_portfolios_have_name(instance, name: MoneyMoney):
    assert name in (a.name for a in instance.portfolios())


def test_transactions_are_present(instance: MoneyMoney):
    account = instance.account("Deutsche Bank")
    assert account is not None
    txns = list(account.transactions())
    assert txns


def test_positions_are_present(instance: MoneyMoney):
    account = instance.portfolio("Comdirect")
    assert account is not None
    assert account.name == "Comdirect"
    positions = list(account.positions())
    assert positions


def test_check_booked_but_unchecked_transactions(instance: MoneyMoney):
    unchecked = 0
    for account in instance.accounts():
        for tx in account.transactions(age=30, booked=True, checked=False):
            assert tx.booked and not tx.checkmark
            unchecked += 1
            tx.set_checkmark(value=True)  # mark this as seen
    assert unchecked == 2

    # now, everything must be checked
    for account in instance.accounts():
        assert not list(account.transactions(age=30, booked=True, checked=False))


def test_transaction_categories(instance: MoneyMoney):
    """Test that transactions have proper categories."""
    categories_found = set()
    for account in instance.accounts():
        for tx in account.transactions():
            if tx.category:
                categories_found.add(tx.category)

    expected_categories = {"Einkommen", "Wohnen", "Steuern", "Lebensmittel"}
    assert expected_categories.issubset(categories_found)


def test_transaction_tags(instance: MoneyMoney):
    """Test transaction tag functionality."""
    account = instance.account("Deutsche Bank")
    assert account is not None

    # Find a transaction with tags
    tx_with_tags = None
    for tx in account.transactions():
        if tx.tags:
            tx_with_tags = tx
            break

    assert tx_with_tags is not None
    assert "tax" in tx_with_tags.tags or "salary" in tx_with_tags.tags


def test_position_data(instance: MoneyMoney):
    """Test portfolio position data."""
    portfolio = instance.portfolio("Comdirect")
    assert portfolio is not None

    positions = list(portfolio.positions())
    assert len(positions) == 2

    # Check that positions have required attributes
    for pos in positions:
        assert hasattr(pos, 'name')
        assert hasattr(pos, 'isin')
        assert hasattr(pos, 'quantity')
        assert hasattr(pos, 'price')
        assert hasattr(pos, 'amount')


def test_categories(instance: MoneyMoney):
    """Test category functionality."""
    categories = list(instance.categories())
    assert len(categories) >= 4

    category_names = {cat.name for cat in categories}
    expected_categories = {"Einkommen", "Wohnen", "Lebensmittel", "Steuern"}
    assert expected_categories.issubset(category_names)


def test_account_balances(instance: MoneyMoney):
    """Test account balance functionality."""
    for account in instance.accounts():
        assert hasattr(account, 'balance')
        assert hasattr(account, 'currency')
        assert account.balance > 0
        assert account.currency == "EUR"


def test_transaction_filtering(instance: MoneyMoney):
    """Test transaction filtering by various criteria."""
    account = instance.account("Deutsche Bank")
    assert account is not None

    # Test filtering by booked status
    booked_txs = list(account.transactions(booked=True))
    unbooked_txs = list(account.transactions(booked=False))
    assert len(booked_txs) > 0
    assert len(unbooked_txs) > 0

    # Test filtering by checked status
    checked_txs = list(account.transactions(checked=True))
    unchecked_txs = list(account.transactions(checked=False))
    assert len(checked_txs) > 0
    assert len(unchecked_txs) > 0

    # Test filtering by category
    income_txs = list(account.transactions(category="Einkommen"))
    assert len(income_txs) > 0
    for tx in income_txs:
        assert tx.category == "Einkommen"
