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

A more complex example, where we only write new transactions.

```
for account in instance.accounts():
    for tx in account.transactions():
        if not tx.checkmark:
	    print(f"New transaction: {tx}")
            tx.set_checkmark(True)
```
