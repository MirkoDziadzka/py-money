from __future__ import annotations

import abc
import datetime
import logging
import plistlib
import json
import re

from typing import Iterable, Optional, List, Dict, Set, Any

from .. import utils


def serialize(obj) -> str:
    """ helper function to serialize an object """
    if isinstance(obj, datetime.datetime):
        return str(obj.date())
    return str(obj)


class Comment:
    TAG_REGEX = re.compile(r"\s*<tag:(?P<tag>[^>]+)>\s*")

    def __init__(self, s: Optional[str]):
        self.text = ""
        self.tags : Set[str] = set()
        self.parse(s or "")
        self.changed = False

    def parse(self, s: str) -> None:
        """ parse a comment into the text part and a list of tags """
        self.tags = set(m.group("tag") for m in self.TAG_REGEX.finditer(s))
        self.text = self.TAG_REGEX.sub("", s).strip()

    def add(self, tag: str) -> None:
        """ add a tag """
        if tag not in self.tags:
            self.changed = True
            self.tags.add(tag)

    def remove(self, tag: str) -> None:
        """ remove a tag """
        if tag in self.tags:
            self.changed = True
            self.tags.remove(tag)

    def __str__(self) -> str:
        res = []
        res.append(self.text.strip())
        for tag in self.tags:
            res.append(f"<tag:{tag}>")
        return (" ".join(res)).strip()


class _Base(abc.ABC):
    """ Base class for Transactions and portfolio positions """
    def __init__(self, account: Account, data):
        self.account = account
        self._backend = account._backend
        self.data = self.normalize(data)

    @classmethod
    def normalize(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        res = {}
        for name, value in data.items():
            if name in cls.IGNORED_ATTRIBUTES:
                continue
            if name not in cls.ATTRIBUTES:
                logging.debug(f" unknown attribute {name} : {value}")
            if isinstance(value, datetime.datetime):
                value = value.date()
                if value <= datetime.date(year=1970, month=1, day=2):
                    continue
            elif name in ("categoryId",):
                continue
            res[name] = value
        return res

    def __getattr__(self, name: str) -> Any:
        if name not in self.ATTRIBUTES:
            raise AttributeError(name)
        return self.data.get(name, None)

    def get(self, name: str) -> Any:
        """ similar to getattr, but never raises an exception """
        return self.data.get(name, None)

    def __repr__(self):
        return json.dumps(self.data, separators=(",", ":"), default=serialize)

class Position(_Base):
    ATTRIBUTES = [
        "id",
        "accountUuid",
        "name",
        "market",  # Xetra, Tradegate, ...
        "type",  # share, bond, ...
        "isin",
        "price",
        "purchasePrice",
        "currencyOfPrice",
        "quantity",
        "amount",
        "currencyOfAmount",
        "absoluteProfit",
        "currencyOfProfit",
        "relativeProfit",
        "tradeTimstamp",
    ]

    IGNORED_ATTRIBUTES = [
        "icon",
    ]


class Transaction(_Base):
    ATTRIBUTES = [
        "id",
        "accountUuid",
        "accountNumber",
        "amount",
        "bankCode",
        "booked",
        "bookingDate",
        "bookingText",
        "category",
        "checkmark",
        "comment",
        "creditorId",
        "currency",
        "endToEndReference",
        "id",
        "mandateReference",
        "name",
        "purpose",
        "valueDate",
    ]
    READ_ONLY_ATTRIBUTES = [
        "id"
    ]

    IGNORED_ATTRIBUTES = [
        "icon",
    ]

    def set_field(self, name: str, value: str) -> None:
        assert name in self.ATTRIBUTES
        assert name not in self.READ_ONLY_ATTRIBUTES
        txid = self.data["id"]
        self._backend.set_transaction_field(txid, name, value)

    @property
    def payee(self) -> str:
        return self.account_number or self.name

    def pass_filter(self, *, booked=None, checked=None, category=None) -> bool:
        if booked is not None and self.booked != booked:
            return False
        if checked is not None and self.checkmark != checked:
            return False
        if category is not None and self.category != category:
            return False
        return True

    def set_checkmark(self, *, value: bool = True) -> None:
        assert isinstance(value, bool)
        if self.data["checkmark"] != value:
            self.set_field("checkmark", "on" if value else "off")

    @property
    def tags(self) -> Set[str]:
        return Comment(self.comment).tags

    def add_tags(self, tag: str, *tags: str) -> None:
        c = Comment(self.comment)
        c.add(tag)
        for t in tags:
            c.add(t)
        self.data["comment"] = str(c)
        if c.changed:
            self.set_field("comment", self.data["comment"])

class Category:
    ATTRIBUTES = [
        "id",
        "name",
        "parentId",
    ]
    IGNORED_ATTRIBUTES = [
        "icon",
    ]

    def __init__(self, account: Account, data):
        self.account = account
        self.data = self.normalize(data)

    @property
    def name(self) -> str:
        return self.data["name"]

    @property
    def id(self) -> str:
        return self.data.get("id") or self.data.get("uuid", "")

    @property
    def parent_id(self) -> Optional[str]:
        return self.data.get("parentId")

    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = {}
        for name, value in data.items():
            if name in self.IGNORED_ATTRIBUTES:
                continue
            if name not in self.ATTRIBUTES:
                logging.debug(f"unknown attribute {name} : {value}")
            if isinstance(value, datetime.datetime):
                value = value.date()
                if value <= datetime.date(year=1970, month=1, day=2):
                    continue
            res[name] = value
        return res

    def __repr__(self):
        return json.dumps(self.data, separators=(",", ":"), default=serialize)



class Account:
    ATTRIBUTES = [
        "id",
        "accountUuid",
        "name",
        "accountNumber",
        "balance",
        "currency",
        "portfolio",
    ]
    IGNORED_ATTRIBUTES = [
        "icon",
    ]


    def __init__(self, backend: BackendInterface, data):
        self._backend = backend
        self.data = self.normalize(data)

    @property
    def name(self) -> str:
        return self.data["name"]

    @property
    def account_number(self) -> str:
        return self.data["accountNumber"]

    @property
    def balance(self) -> float:
        return self.data["balance"][0][0]

    @property
    def currency(self) -> str:
        return self.data["balance"][0][1]

    @property
    def is_portfolio(self) -> bool:
        return self.data["portfolio"]

    @classmethod
    def normalize(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        res = {}
        for name, value in data.items():
            if name in cls.IGNORED_ATTRIBUTES:
                continue
            if name not in cls.ATTRIBUTES:
                logging.debug(f"unknown attribute {name} : {value}")
            if isinstance(value, datetime.datetime):
                value = value.date()
                if value <= datetime.date(year=1970, month=1, day=2):
                    continue
            elif name in ("categoryId",):
                continue
            res[name] = value
        return res

    def transactions(self, age=90, start_date=None, end_date=None, **tx_filter) -> Iterable[Transaction]:
        """extract transactions from the account which match the filter

        if start_data is given, it is generated from age
        if end_data is not give, no end_date will be assumed.
        other argumens are treated as filter on the transactions. Currently supported:
        - booked - the transaction is marked as booked or not yet booked
        - checked - the checkmark is True (or False)
        - category - the value of the category field matches the given argument
        """
        if self.is_portfolio:
            return

        if start_date is None:
            start_date = datetime.date.today() - datetime.timedelta(days=age)

        for tx_data in self._backend.get_transactions(self.account_number, start_date, end_date):
            tx = Transaction(self, tx_data)
            if tx.pass_filter(**tx_filter):
                yield tx

    def positions(self) -> Iterable[Position]:
        """extract positions from a portfolio """
        if not self.is_portfolio:
            return
        for tx_data in self._backend.get_positions(self.account_number):
            yield Position(self, tx_data)

    def __repr__(self):
        return json.dumps(self.data, separators=(",", ":"), default=serialize)


class BackendInterface(abc.ABC):
    """ generoc inteface for a MoneyMoney Backend """
    # pylint: disable=unused-argument

    @abc.abstractmethod
    def get_accounts(self):
        ...

    @abc.abstractmethod
    def get_transactions(self, account: str, start_date: datetime.date, end_date: Optional[datetime.date]):
        ...

    @abc.abstractmethod
    def get_positions(self, account: str):
        ...

    @abc.abstractmethod
    def set_transaction_field(self, txid: str, name: str, value: str):
        ...

    @abc.abstractmethod
    def get_categories(self):
        ...


class Backend(BackendInterface):
    MAC_APP_NAME = "MoneyMoney"

    @staticmethod
    def run_apple_script(script: str) -> bytes:
        return utils.applescript(script)

    def get_accounts(self) -> List[Dict[str, Any]]:
        script = f'tell application "{self.MAC_APP_NAME}" to export accounts'
        data = self.run_apple_script(script)
        return plistlib.loads(data)

    def get_transactions(self, account: str, start_date, end_date):
        cmd = []
        cmd += [f'tell application "{self.MAC_APP_NAME}" to export transactions']
        cmd += [f'from account "{account}"']
        cmd += [f'from date "{start_date.strftime("%d/%m/%Y")}"']
        if end_date is not None:
            cmd += [f'to date "{end_date.strftime("%d/%m/%Y")}"']
        cmd += ['as "plist"']
        data = self.run_apple_script(" ".join(cmd))
        return plistlib.loads(data).get("transactions", [])

    def get_positions(self, account: str):
        cmd = []
        cmd += [f'tell application "{self.MAC_APP_NAME}" to export portfolio']
        cmd += [f'from account "{account}"']
        cmd += ['as "plist"']

        res = self.run_apple_script(" ".join(cmd))
        tx_data = plistlib.loads(res)
        return tx_data.get("portfolio", [])

    def get_categories(self):
        cmd = []
        cmd += [f'tell application "{self.MAC_APP_NAME}" to export categories']
        # cmd += ['as "plist"']
        res = self.run_apple_script(" ".join(cmd))
        return plistlib.loads(res)

    def set_transaction_field(self, txid: str, name: str, value: str):
        cmd = [
            f'tell application "{self.MAC_APP_NAME}"',
            f"to set transaction id {txid}",
            f'{name} to "{value}"',
        ]
        self.run_apple_script(" ".join(cmd))


class MoneyMoney:
    """ An interface to the MoneyMoney app """
    def __init__(self, backend: BackendInterface = Backend()):
        self._backend = backend
        self.data = self._backend.get_accounts()
        self._categories = self._backend.get_categories()

    def _accounts(self) -> Iterable[Account]:
        """ return all accounts """
        for account in self.data:
            if account.get("group") is not True:
                yield Account(self._backend, account)

    def accounts(self) -> Iterable[Account]:
        return (account for account in self._accounts() if account.is_portfolio is False)

    def account(self, name: str) -> Optional[Account]:
        for account in self.accounts():
            if account.name == name:
                return account
        return None

    def portfolios(self) -> Iterable[Account]:
        return (account for account in self._accounts() if account.is_portfolio is True)

    def portfolio(self, name: str) -> Optional[Account]:
        for portfolio in self.portfolios():
            if portfolio.name == name:
                return portfolio
        return None

    def transactions(self, *args, **kwargs):
        for account in self.accounts():
            yield from account.transactions(*args, **kwargs)

    def categories(self) -> Iterable[Category]:
        for category in self._categories:
            yield Category(self, category)
