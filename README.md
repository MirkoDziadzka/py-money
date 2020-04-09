# py-money

A Python interface to MoneyMoney

# Examples

```py
import money

instance = money.connect(money.MoneyMoney)

for account in instance.accounts():
    for transaction in account.transactions():
        if amount := transaction.amount > 0:
	    print(f"Transfered {amount:.2f}€ from {account.name} to {transaction.payee})
```
