import csv
import random

import money

instance = money.MoneyMoney()


FILENAME = "out.csv"
FIELDS = [
    "account",
    "id",
    "accountNumber",
    "bankCode",
    "booked",
    "amount",
    "currency",
    "name",
    "bookingText",
    "purpose",
    "endToEndReference",
    "creditorId",
    "mandateReference",
    "bookingDate",
    "valueDate",
    "checkmark"
]


with open(FILENAME, "w") as fd:
    # writer = csv.DictWriter(fd, FIELDS, restval='', extrasaction='ignore')
    writer = csv.DictWriter(fd, FIELDS, restval='', extrasaction='raise')
    writer.writeheader()

    for account in instance.accounts():
        for tx in account.transactions():
            if not tx.booked:
                print(f"Ignore unbooked transaction: {tx}")
                continue
            row = dict(tx.data, account=tx.account.name)
            writer.writerow(row)
            if not tx.checkmark:
                print(f"New transaction: {tx}")
                tx.set_checkmark(value=True)

