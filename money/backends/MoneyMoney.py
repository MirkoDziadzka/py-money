
import datetime
import plistlib
import json

from .. import utils


def serialize(obj):
    if isinstance(obj, datetime.datetime):
        return str(obj.date())
    return str(obj)

def run_apple_script(script):
    return utils.applescript(script)

def _transactions(account=None, *, age=90, start_date=None, end_date=None, **tx_filter):
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
        cmd += [f'from account "{account.accountNumber}"']
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

class Transaction:
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
            "valueDate",
            ]

    def __init__(self, account, data):
        self.account = account
        self.data = self.normalize(data)

    @classmethod
    def normalize(cls, data):
        res = {}
        for k,v in data.items():
            if isinstance(v, datetime.datetime):
                v = v.date()
                if v <= datetime.date(year=1970, month=1, day=2):
                    continue
                pass
            elif k in ("comment", "categoryId"):
                continue
            res[k] = v
        return res

    def __getattr__(self, name):
        if name not in self.ATTRIBUTES:
            raise AttributeError(name)
        return self.data.get(name, None)

    @property
    def payee(self):
        return self.accountNumber or self.name

    def pass_filter(self, *, booked=None, checked=None, category=None):
        if booked is not None and self.booked != booked:
            return False
        if checked is not None and self.checkmark != checked:
            return False
        if category is not None and self.category != category:
            return False
        return True

    def set_checkmark(self, *, value=True):
        assert isinstance(value, bool)
        if self.data["checkmark"] != value:
            txid = self.data["id"]
            onoff = "on" if value else "off"
            cmd = f'tell application "MoneyMoney" to set transaction id {txid} checkmark to "{onoff}"'
            res = run_apple_script(cmd)
            self.data["checkmark"] = value

    def __repr__(self):
        return json.dumps(self.data, separators=(',', ':'), default=serialize)


class Account:
    def __init__(self, data):
        self.data = data

    @property
    def name(self):
        return self.data["name"]

    @property
    def accountNumber(self):
        return self.data["accountNumber"]


    def transactions(self, *args, **kwargs):
        return _transactions(account=self, *args, **kwargs)

    def __repr__(self):
        return json.dumps(self.data, separators=(',', ':'), default=serialize)


class MoneyMoney:
    def __init__(self):
        res = run_apple_script('tell application "MoneyMoney" to export accounts')
        # convert res to a python form .. this is ugly
        self.data = plistlib.loads(res)

    def accounts(self):
        for account in self.data:
            if account.get("accountNumber"):
                yield(Account(account))

    def transactions(self, *args, **kwargs):
        return _transactions(account=None, *args, **kwargs)





