
import datetime
import plistlib

import applescript


def run_apple_script(script):
    res = applescript.run(script)
    if res.code > 0:
        raise Exception(f'AppleScript Error: {res.err["NSAppleScriptErrorMessage"]}')
    return res.out

class Transaction:
    def __init__(self, data):
        self.data = data
        print(data)

    @property
    def amount(self):
        return self.data["amount"]

    @property
    def name(self):
        return self.data["name"]

    @property
    def payee(self):
        return self.data["accountNumber"]


class Account:
    def __init__(self, data):
        self.data = data
        self.tx_data = None

    @property
    def name(self):
        return self.data["accountNumber"]

    def transactions(self):
        now = datetime.datetime.now()
        start = now - datetime.timedelta(days=7)
        print(start, now)
        cmd = f'tell application "MoneyMoney" to export transactions from account "{self.data["accountNumber"]}" from date "{start.strftime("%d/%m/%Y")}" to data "{now.strftime("%d/%m/%Y")}" as "plist"'
        print(cmd)
        res = run_apple_script(cmd)
        self.tx_data = plistlib.loads(res.encode("utf-8"))
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





