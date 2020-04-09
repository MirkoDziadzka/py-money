import money

instance = money.MoneyMoney()

for account in instance.accounts():
    for tx in account.transactions():
        if tx.amount > 0:
            print(f"Transfered {tx.amount:.2f}€ from {account.name} to {tx.payee}")

