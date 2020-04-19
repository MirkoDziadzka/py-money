import csv
import datetime

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
    "category",
    "bookingDate",
    "valueDate",
    "checkmark"
]

#
# Transactions of the last 7 days
#

print("Show all new, booked and unchecked transactions")
for account in instance.accounts():
    for tx in account.transactions(age=30, booked=True, checked=False):
        assert tx.booked == True and tx.checkmark == False
        print(f'Found new transaction: {account.name} {tx.bookingDate} {tx.amount:10.2f} {tx.currency} {tx.name}')
        tx.set_checkmark(value=True)  # mark this as seen


category = "Spende"

print(f"Show all transactions which are marked as category '{category}'")
for tx in instance.transactions(age=30, booked=True, category=category):
    assert tx.booked == True and tx.category == category
    print(f'Found new transaction: {tx.bookingDate} {tx.amount:10.2f} {tx.currency} {tx.name}')

print(f"Convert all transactions to csv '{FILENAME}'")

with open(FILENAME, "w") as fd:
    writer = csv.DictWriter(fd, FIELDS, restval='', extrasaction='raise')
    writer.writeheader()

    for account in instance.accounts():
        print(f"Writing data for account {account.name} ...", end='', flush=True)
        count = 0
        begin_of_time = datetime.date(year=1970, month=1, day=1)
        for tx in account.transactions(start_date=begin_of_time, booked=True):
            assert tx.booked == True
            row = dict(tx.data, account=tx.account.name)
            writer.writerow(row)
            count += 1
        print(f"wrote {count} entries")

