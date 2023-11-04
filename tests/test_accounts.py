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

