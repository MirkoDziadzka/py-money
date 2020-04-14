
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

class Transaction:
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
            elif k == "comment":
                continue
            res[k] = v
        return res

    @property
    def amount(self):
        return self.data["amount"]

    @property
    def name(self):
        return self.data["name"]

    @property
    def payee(self):
        return self.data.get("accountNumber") or self.name

    @property
    def booked(self):
        return self.data["booked"]

    @property
    def checkmark(self):
        return self.data["checkmark"]

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

    def transactions(self):
        start = (datetime.datetime.now() - datetime.timedelta(days=90))
        cmd = f'tell application "MoneyMoney" to export transactions from account "{self.data["accountNumber"]}" from date "{start.strftime("%d/%m/%Y")}" as "plist"'
        res = run_apple_script(cmd)
        tx_data = plistlib.loads(res)
        for tx in tx_data.get("transactions", []):
            yield Transaction(self, tx)

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





