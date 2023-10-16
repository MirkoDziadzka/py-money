""" unit tests
"""

from datetime import date
import os.path
from typing import Optional

import pytest
import yaml

from money import MoneyMoney
from money.backends.MoneyMoney import BackendInterface

TESTDIR = os.path.dirname(__file__)


class MockedBackend(BackendInterface):
    def __init__(self, data):
        self.data = data

    def get_accounts(self):
        return self.data["accounts"]

    def get_positions(self, account: str):
        return self.data["positions"][account]

    def get_transactions(self, account: str, start_date: date, end_date: Optional[date]):
        return self.data["transactions"][account]

    def set_transaction_field(self, txid: str, name: str, value: str):
        print(txid, name, value)
        for txlist in self.data["transactions"].values():
            for tx in txlist:
                print(tx)
                if tx["id"] == txid:
                    if name == "checkmark":
                        tx["checkmark"] = value == "on"
                    else:
                        raise NotImplementedError


# pylint: disable=redefined-outer-name
@pytest.fixture
def instance() -> MoneyMoney:
    with open(os.path.join(TESTDIR, "backend_config.yml"), "rb") as fd:
        data = yaml.safe_load(fd.read())
        backend = MockedBackend(data)
        return MoneyMoney(backend=backend)

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

