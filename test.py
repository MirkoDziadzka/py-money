import csv

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
            row = dict(tx.data, account=account.name)
            writer.writerow(row)
            print(tx)
            # print(f"{account.name} -> {tx.payee}: {tx.amount:0.2f}")

