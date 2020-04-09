
import datetime
import plistlib
import json

import applescript


def serialize(obj):
    if isinstance(obj, datetime.datetime):
        return str(obj.date())

def run_apple_script(script):
    res = applescript.run(script)
    if res.code > 0:
        raise Exception(f"Apple Script: {res.err}")
    return res.out

class Transaction:
    def __init__(self, data):
        self.data = data

    @property
    def amount(self):
        return self.data["amount"]

    @property
    def name(self):
        return self.data["name"]

    @property
    def payee(self):
        return self.data.get("accountNumber") or self.name

    def __repr__(self):
        return json.dumps(self.data, separators=(',', ':'), default=serialize)


class Account:
    def __init__(self, data):
        self.data = data
        self.tx_data = dict(transactions=[])

    @property
    def name(self):
        return self.data["accountNumber"]

    def transactions(self):
        now = datetime.datetime.now()
        start = now - datetime.timedelta(days=90)
        cmd = f'tell application "MoneyMoney" to export transactions from account "{self.data["accountNumber"]}" from date "{start.strftime("%d/%m/%Y")}" to data "{now.strftime("%d/%m/%Y")}" as "plist"'
        try:
            res = run_apple_script(cmd)
            self.tx_data = plistlib.loads(res.encode("utf-8"))
        except:
            pass
        for tx in self.tx_data.get("transactions", []):
            yield Transaction(tx)


class MoneyMoney:
    def __init__(self):
        res = run_apple_script('tell application "MoneyMoney" to export accounts')
        # convert res to a python form .. this is ugly
        self.data = plistlib.loads(res.encode("utf-8"))

    def accounts(self):
        for account in self.data:
            if account.get("accountNumber"):
                yield(Account(account))





