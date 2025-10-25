"""
Test utilities for mocking MoneyMoney application responses.

This module provides utilities to create mock data and test scenarios
for the MoneyMoney library.
"""

import os
import yaml
from datetime import date, datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from money.backends.MoneyMoney import BackendInterface


@dataclass
class MockTransactionData:
    """Data class for creating mock transaction data."""
    id: str
    account_number: str
    amount: float
    currency: str = "EUR"
    name: str = "Test Transaction"
    booked: bool = True
    checkmark: bool = False
    category: Optional[str] = None
    comment: str = ""
    booking_date: Optional[date] = None
    value_date: Optional[date] = None
    purpose: str = ""
    bank_code: str = "TEST"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format expected by MoneyMoney backend."""
        return {
            "id": self.id,
            "accountNumber": self.account_number,
            "amount": self.amount,
            "currency": self.currency,
            "name": self.name,
            "booked": self.booked,
            "checkmark": self.checkmark,
            "category": self.category,
            "comment": self.comment,
            "bookingDate": self.booking_date or date.today(),
            "valueDate": self.value_date or date.today(),
            "purpose": self.purpose,
            "bankCode": self.bank_code,
        }


@dataclass
class MockAccountData:
    """Data class for creating mock account data."""
    name: str
    account_number: str
    balance: float
    currency: str = "EUR"
    is_portfolio: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format expected by MoneyMoney backend."""
        return {
            "name": self.name,
            "accountNumber": self.account_number,
            "balance": [[self.balance, self.currency]],
            "currency": self.currency,
            "portfolio": self.is_portfolio,
        }


@dataclass
class MockPositionData:
    """Data class for creating mock position data."""
    name: str
    isin: str
    quantity: int
    price: float
    purchase_price: float
    currency: str = "USD"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format expected by MoneyMoney backend."""
        amount = self.quantity * self.price
        profit = (self.price - self.purchase_price) * self.quantity
        return {
            "id": f"pos_{self.isin}",
            "name": self.name,
            "isin": self.isin,
            "market": "NASDAQ",
            "type": "share",
            "quantity": self.quantity,
            "price": self.price,
            "purchasePrice": self.purchase_price,
            "currencyOfPrice": self.currency,
            "amount": amount,
            "currencyOfAmount": self.currency,
            "absoluteProfit": profit,
            "currencyOfProfit": self.currency,
            "relativeProfit": (profit / (self.purchase_price * self.quantity)) * 100,
            "tradeTimestamp": date.today().strftime("%Y-%m-%d"),
        }


@dataclass
class MockCategoryData:
    """Data class for creating mock category data."""
    name: str
    parent_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format expected by MoneyMoney backend."""
        return {
            "id": f"cat_{self.name.lower().replace(' ', '_')}",
            "name": self.name,
            "parentId": self.parent_id,
        }


class MockDataBuilder:
    """Builder class for creating comprehensive mock data sets."""
    
    def __init__(self):
        self.accounts: List[MockAccountData] = []
        self.transactions: Dict[str, List[MockTransactionData]] = {}
        self.positions: Dict[str, List[MockPositionData]] = {}
        self.categories: List[MockCategoryData] = []
    
    def add_account(self, account: MockAccountData) -> 'MockDataBuilder':
        """Add an account to the mock data."""
        self.accounts.append(account)
        return self
    
    def add_transaction(self, account_number: str, transaction: MockTransactionData) -> 'MockDataBuilder':
        """Add a transaction to the mock data."""
        if account_number not in self.transactions:
            self.transactions[account_number] = []
        self.transactions[account_number].append(transaction)
        return self
    
    def add_position(self, account_number: str, position: MockPositionData) -> 'MockDataBuilder':
        """Add a position to the mock data."""
        if account_number not in self.positions:
            self.positions[account_number] = []
        self.positions[account_number].append(position)
        return self
    
    def add_category(self, category: MockCategoryData) -> 'MockDataBuilder':
        """Add a category to the mock data."""
        self.categories.append(category)
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build the complete mock data dictionary."""
        return {
            "accounts": [account.to_dict() for account in self.accounts],
            "transactions": {
                acc_num: [tx.to_dict() for tx in txs]
                for acc_num, txs in self.transactions.items()
            },
            "positions": {
                acc_num: [pos.to_dict() for pos in positions]
                for acc_num, positions in self.positions.items()
            },
            "categories": [cat.to_dict() for cat in self.categories],
        }
    
    def save_to_file(self, filepath: str) -> None:
        """Save the mock data to a YAML file."""
        data = self.build()
        with open(filepath, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)


def create_sample_data() -> MockDataBuilder:
    """Create a sample data set for testing."""
    builder = MockDataBuilder()
    
    # Add sample accounts
    builder.add_account(MockAccountData("Test Bank", "TB123456", 1500.00))
    builder.add_account(MockAccountData("Test Broker", "TB789012", 5000.00, is_portfolio=True))
    
    # Add sample categories
    builder.add_category(MockCategoryData("Income"))
    builder.add_category(MockCategoryData("Expenses"))
    builder.add_category(MockCategoryData("Food", "Expenses"))
    builder.add_category(MockCategoryData("Transport", "Expenses"))
    
    # Add sample transactions
    today = date.today()
    builder.add_transaction("TB123456", MockTransactionData(
        id="tx001",
        account_number="TB123456",
        amount=2500.00,
        name="Salary",
        category="Income",
        comment="Monthly salary <tag:salary>",
        booking_date=today - timedelta(days=1)
    ))
    
    builder.add_transaction("TB123456", MockTransactionData(
        id="tx002",
        account_number="TB123456",
        amount=-100.00,
        name="Grocery Store",
        category="Food",
        comment="Weekly shopping",
        booking_date=today - timedelta(days=2)
    ))
    
    # Add sample positions
    builder.add_position("TB789012", MockPositionData(
        name="Apple Inc.",
        isin="US0378331005",
        quantity=10,
        price=150.00,
        purchase_price=140.00
    ))
    
    return builder


def create_test_scenarios() -> Dict[str, MockDataBuilder]:
    """Create various test scenarios for different testing needs."""
    scenarios = {}
    
    # Empty data scenario
    scenarios["empty"] = MockDataBuilder()
    
    # Single account scenario
    single_account = MockDataBuilder()
    single_account.add_account(MockAccountData("Single Account", "SA001", 1000.00))
    scenarios["single_account"] = single_account
    
    # High transaction volume scenario
    high_volume = MockDataBuilder()
    high_volume.add_account(MockAccountData("High Volume Bank", "HV001", 10000.00))
    high_volume.add_category(MockCategoryData("Income"))
    high_volume.add_category(MockCategoryData("Expenses"))
    
    # Add many transactions
    for i in range(100):
        high_volume.add_transaction("HV001", MockTransactionData(
            id=f"tx_{i:03d}",
            account_number="HV001",
            amount=10.00 + i,
            name=f"Transaction {i}",
            category="Expenses" if i % 2 == 0 else "Income",
            booking_date=date.today() - timedelta(days=i)
        ))
    
    scenarios["high_volume"] = high_volume
    
    # Complex portfolio scenario
    portfolio = MockDataBuilder()
    portfolio.add_account(MockAccountData("Investment Account", "IA001", 50000.00, is_portfolio=True))
    portfolio.add_category(MockCategoryData("Stocks"))
    portfolio.add_category(MockCategoryData("Bonds"))
    
    # Add various positions
    stocks = [
        ("Apple Inc.", "US0378331005", 10, 150.00, 140.00),
        ("Microsoft Corp.", "US5949181045", 5, 300.00, 280.00),
        ("Google LLC", "US02079K3059", 2, 2500.00, 2400.00),
    ]
    
    for name, isin, qty, price, purchase_price in stocks:
        portfolio.add_position("IA001", MockPositionData(
            name=name,
            isin=isin,
            quantity=qty,
            price=price,
            purchase_price=purchase_price
        ))
    
    scenarios["complex_portfolio"] = portfolio
    
    return scenarios


class MockBackendFactory:
    """Factory for creating mock backends with different configurations."""
    
    @staticmethod
    def create_from_file(filepath: str) -> 'MockedBackend':
        """Create a mock backend from a YAML file."""
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        return MockedBackend(data)
    
    @staticmethod
    def create_from_builder(builder: MockDataBuilder) -> 'MockedBackend':
        """Create a mock backend from a MockDataBuilder."""
        return MockedBackend(builder.build())
    
    @staticmethod
    def create_sample() -> 'MockedBackend':
        """Create a mock backend with sample data."""
        return MockBackendFactory.create_from_builder(create_sample_data())


class MockedBackend(BackendInterface):
    """Enhanced mock backend for testing."""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
    
    def get_accounts(self):
        return self.data.get("accounts", [])
    
    def get_positions(self, account: str):
        return self.data.get("positions", {}).get(account, [])
    
    def get_transactions(self, account: str, start_date: date, end_date: Optional[date]):
        transactions = self.data.get("transactions", {}).get(account, [])
        
        # Filter by date range if provided
        filtered_transactions = []
        for tx in transactions:
            tx_date = tx.get("bookingDate", tx.get("valueDate"))
            if isinstance(tx_date, str):
                tx_date = datetime.strptime(tx_date, "%Y-%m-%d").date()
            elif isinstance(tx_date, datetime):
                tx_date = tx_date.date()
            
            if start_date <= tx_date <= (end_date or date.today()):
                filtered_transactions.append(tx)
        
        return filtered_transactions
    
    def set_transaction_field(self, txid: str, name: str, value: str):
        """Update a transaction field in the mock data."""
        for txlist in self.data.get("transactions", {}).values():
            for tx in txlist:
                if tx["id"] == txid:
                    if name == "checkmark":
                        tx["checkmark"] = value == "on"
                    elif name == "comment":
                        tx["comment"] = value
                    elif name == "category":
                        tx["category"] = value
                    else:
                        tx[name] = value
                    return
    
    def get_categories(self):
        return self.data.get("categories", [])