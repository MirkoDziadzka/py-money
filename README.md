# py-money

A Python interface to MoneyMoney

# Examples

```py
import money

instance = money.MoneyMoney()

for account in instance.accounts():
    for tx in account.transactions():
        print(f"{account.name} -> {tx.payee}: {tx.amount:0.2f}")
```
