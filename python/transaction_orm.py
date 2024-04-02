from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TransactionType(Enum):
    BUY = 'Buy'
    CONVERT_FROM = 'Convert (From)'
    CONVERT_TO = 'Convert (To)'
    RECEIVE = 'Receive'
    SELL = 'Sell'
    SEND = 'Send'
    STAKING_INCOME = 'Staking Income'
    UNWRAP = 'Unwrap'

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    transaction_ts = Column(DateTime)
    transaction_type = Column(String)
    asset = Column(String)
    amount = Column(Float)
    asset_transaction_value = Column(Float)
    asset_unit_price = Column(Float)
    fees = Column(Float)
    description = Column(String)
    account_starting_balance = Column(Float)
    account_ending_balance = Column(Float)

    def __repr__(self):
        return f"<Transaction(id={self.id}, transaction_ts={self.transaction_ts}, transaction_type={self.transaction_type}, asset={self.asset}, amount={self.amount}, asset_transaction_value={self.asset_transaction_value}, asset_unit_price={self.asset_unit_price}, fees={self.fees}, description={self.description}, account_starting_balance={self.account_starting_balance}, account_ending_balance={self.account_ending_balance})>"

    @property
    def is_convert_from(self):
        return self.transaction_type == TransactionType.CONVERT_FROM.value

    @property
    def is_convert_to(self):
        return self.transaction_type == TransactionType.CONVERT_TO.value
