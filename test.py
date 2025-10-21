import csv
import datetime

import money

instance = money.MoneyMoney()


FILENAME = "out.csv"
FIELDS = [
    "account",
    "id",
    "accountNumber",
    "accountUuid",
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
    "category",
    "categoryUuid",
    "bookingDate",
    "valueDate",
    "comment",
    "checkmark",
]

#
# Transactions of the last 7 days
#

print("Show all new, booked and unchecked transactions")
for account in instance.accounts():
    print(f"Checking account {account.name}")
    for tx in account.transactions(age=30, booked=True, checked=False):
        assert tx.booked and not tx.checkmark
        print(
            f"Found new transaction: {tx.id} {account.name} {tx.bookingDate} {tx.amount:10.2f} {tx.currency} {tx.name}"
        )
        tx.set_checkmark(value=True)  # mark this as seen

print("Check all transactions and tag all transaction with a given word")
for account in instance.accounts():
    for tx in account.transactions(age=7, booked=True):
        if tx.name and "Medecins Sans Frontieres" in tx.name:
            tx.add_tags("tax-relevant")


category = "Spende"

print(f"Show all transactions which are marked as category '{category}'")
for tx in instance.transactions(age=30, booked=True, category=category):
    assert tx.booked and tx.category == category
    print(
        f"Found new transaction: {tx.bookingDate} {tx.amount:10.2f} {tx.currency} {tx.name}"
    )

print(f"Convert all transactions to csv '{FILENAME}'")

with open(FILENAME, "w", encoding="utf-8") as fd:
    writer = csv.DictWriter(fd, FIELDS, restval="", extrasaction="raise")
    writer.writeheader()

    for account in instance.accounts():
        print(f"Writing data for account {account.name} ...", end="", flush=True)
        count = 0
        begin_of_time = datetime.date(year=2000, month=1, day=1)
        for tx in account.transactions(start_date=begin_of_time, booked=True):
            assert tx.booked is True
            row = dict(tx.data, account=tx.account.name)
            writer.writerow(row)
            count += 1
        print(f"wrote {count} entries")


print("Check all Portfolios")
for account in instance.portfolios():
    print(f"Checking portfolio: {account.name}")
    for p in account.positions():
        print(f"Have {p.quantity} {p.type}s from '{p.name}' at price {p.price} {p.currencyOfPrice} " +
              f"resulting in a value of {p.amount} {p.currencyOfAmount}")
