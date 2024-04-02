CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    transaction_ts TIMESTAMP,
    transaction_type TEXT,
    asset TEXT,
    amount REAL,
    asset_transaction_value REAL,
    asset_unit_price REAL,
    fees REAL,
    description TEXT,
    account_starting_balance REAL,
    account_ending_balance REAL
);