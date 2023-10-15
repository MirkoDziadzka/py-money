from __future__ import annotations

import abc
import datetime
import plistlib
import json
import re

from typing import Iterable, Set, Optional

from .. import utils

MAC_APP_NAME = "MoneyMoney"


def serialize(obj) -> str:
    if isinstance(obj, datetime.datetime):
        return str(obj.date())
    return str(obj)


def run_apple_script(script: str) -> bytes:
    return utils.applescript(script)


class Comment:
    TAG_REGEX = re.compile(r"\s*<tag:(?P<tag>[^>]+)>\s*")

    def __init__(self, s: Optional[str]):
        self.text = ""
        self.tags : Set[str] = set()
        self.parse(s or "")
        self.changed = False

    def parse(self, s: str) -> None:
        self.tags = set(m.group("tag") for m in self.TAG_REGEX.finditer(s))
        self.text = self.TAG_REGEX.sub("", s).strip()

    def add(self, tag: str):
        if tag not in self.tags:
            self.changed = True
            self.tags.add(tag)

    def __str__(self):
        res = []
        res.append(self.text.strip())
        for tag in self.tags:
            res.append(f"<tag:{tag}>")
        return (" ".join(res)).strip()


def _transactions(
    account=None, *, age=90, start_date=None, end_date=None, **tx_filter
) -> Iterable[Transaction]:
    """extract transactions from MoneyMoney which match the filter

    if start_data is given, it is generated from age
    if end_data is not give, no end_date will be assumed.
    other argumens are treated as filter on the transactions. Currently supported:
    - booked - the transaction is marked as booked or not yet booked
    - checked - the checkmark is True (or False)
    - category - the value of the category field matches the given argument

    if account is given, it is expected to be an Account object
    and only transactions from this account will be fetched.
    """

    if start_date is None:
        start_date = datetime.date.today() - datetime.timedelta(days=age)
    cmd = []
    cmd += ['tell application "MoneyMoney" to export transactions']
    if account is not None:
        cmd += [f'from account "{account.account_number}"']
    cmd += [f'from date "{start_date.strftime("%d/%m/%Y")}"']
    if end_date is not None:
        cmd += [f'to date "{end_date.strftime("%d/%m/%Y")}"']
    cmd += ['as "plist"']
    res = run_apple_script(" ".join(cmd))
    tx_data = plistlib.loads(res)
    for tx_data in tx_data.get("transactions", []):
        tx = Transaction(account, tx_data)
        if tx.pass_filter(**tx_filter):
            yield tx


class _Base(abc.ABC):
    def __init__(self, account: Account, data):
        self.account = account
        self.data = self.normalize(data)

    @classmethod
    def normalize(cls, data):
        res = {}
        for name, value in data.items():
            if isinstance(value, datetime.datetime):
                value = value.date()
                if value <= datetime.date(year=1970, month=1, day=2):
                    continue
            elif name in ("categoryId",):
                continue
            res[name] = value
        return res

    def __getattr__(self, name):
        if name not in self.ATTRIBUTES:
            raise AttributeError(name)
        return self.data.get(name, None)

    def __repr__(self):
        return json.dumps(self.data, separators=(",", ":"), default=serialize)

class Position(_Base):
    ATTRIBUTES = [
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


class Transaction(_Base):
    ATTRIBUTES = [
        "accountNumber",
        "amount",
        "bankCode",
        "booked",
        "bookingDate",
        "bookingText",
        "category",
        "checkmark",
        "creditorId",
        "currency",
        "endToEndReference",
        "mandateReference",
        "name",
        "purpose",
        "comment",
        "valueDate",
    ]


    def set_field(self, name: str, value: str):
        assert name in self.ATTRIBUTES
        txid = self.data["id"]
        cmd = " ".join(
            [
                f'tell application "{MAC_APP_NAME}"',
                f"to set transaction id {txid}",
                f'{name} to "{value}"',
            ]
        )
        run_apple_script(cmd)


    @property
    def payee(self) -> str:
        return self.account_number or self.name

    def pass_filter(self, *, booked=None, checked=None, category=None):
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


class Account:
    def __init__(self, data):
        self.data = data

    @property
    def name(self) -> str:
        return self.data["name"]

    @property
    def account_number(self) -> str:
        return self.data["accountNumber"]

    @property
    def balance(self):
        return self.data["balance"][0][0]

    @property
    def currency(self):
        return self.data["balance"][0][1]

    @property
    def is_portfolio(self):
        return self.data["portfolio"]

    def transactions(self, *args, **kwargs):
        if not self.is_portfolio:
            return _transactions(account=self, *args, **kwargs)
        return []

    def positions(self) -> Iterable[Position]:
        """extract positions from a portfolio """
        if not self.is_portfolio:
            return
        cmd = []
        cmd += ['tell application "MoneyMoney" to export portfolio']
        cmd += [f'from account "{self.account_number}"']
        cmd += ['as "plist"']

        res = run_apple_script(" ".join(cmd))
        tx_data = plistlib.loads(res)
        for tx_data in tx_data.get("portfolio", []):
            yield Position(self, tx_data)

    def __repr__(self):
        return json.dumps(self.data, separators=(",", ":"), default=serialize)


class MoneyMoney:
    def __init__(self):
        res = run_apple_script('tell application "MoneyMoney" to export accounts')
        # convert res to a python form .. this is ugly
        self.data = plistlib.loads(res)

    def _accounts(self) -> Iterable[Account]:
        for account in self.data:
            if account.get("group") is not True:
                yield Account(account)

    def accounts(self) -> Iterable[Account]:
        return (account for account in self._accounts() if account.is_portfolio is False)

    def portfolios(self) -> Iterable[Account]:
        return (account for account in self._accounts() if account.is_portfolio is True)

    def transactions(self, *args, **kwargs):
        return _transactions(account=None, *args, **kwargs)
