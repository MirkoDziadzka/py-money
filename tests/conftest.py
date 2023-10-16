import os
from datetime import date
from typing import Optional

import pytest
from yaml import safe_load

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


@pytest.fixture
def instance() -> MoneyMoney:
    with open(os.path.join(TESTDIR, "backend_config.yml"), "rb") as fd:
        data = safe_load(fd.read())
        backend = MockedBackend(data)
        return MoneyMoney(backend=backend)