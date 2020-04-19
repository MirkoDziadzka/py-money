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


Only print new transactions (checked=False) which are already booked.
After printing them out, set the state to 'checked' so that they
will not be seen in the next invocation.
```py
for account in instance.accounts():
    for tx in account.transactions(age=90, booked=True, checked=False):
        print(f"New transaction: {tx}")
        tx.set_checkmark()
```
