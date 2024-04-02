import csv
import sqlite3
import os
from transaction_orm import Transaction, TransactionType
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker
from datetime import datetime

class TransactionDatabase:
    TIME_FORMAT = "%Y-%m-%d %H:%M:%S %Z"
    def __init__(self, db_file):
        self.db_file = db_file

    def create_database(self, ddl_dir):
        """Create a database and execute DDL scripts from a directory."""
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Get a list of DDL files in the directory
        ddl_files = [file for file in os.listdir(ddl_dir) if file.endswith('.sql')]
        ddl_files.sort()  # Sort the files alphabetically

        # Check if migrations table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='migrations';")
        table_exists = cursor.fetchone()

        if not table_exists:
            # Create migrations table if it doesn't exist
            cursor.execute("""
                CREATE TABLE migrations (
                    id INTEGER PRIMARY KEY,
                    executed_at_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    migration_name TEXT
                );
            """)

        # Execute DDL scripts in alphabetical order
        for file in ddl_files:
            # Extract the migration name from the filename
            migration_name = os.path.splitext(file)[0]

            # Check if migration has already been executed
            cursor.execute("SELECT * FROM migrations WHERE migration_name = ?", (migration_name,))
            migration_exists = cursor.fetchone()

            if not migration_exists:
                # Read the DDL script from the file
                with open(os.path.join(ddl_dir, file), 'r') as f:
                    ddl_script = f.read()
                    cursor.executescript(ddl_script)

                # Record the execution of the DDL script in the migrations table
                executed_at_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute("INSERT INTO migrations (executed_at_date, migration_name) VALUES (?, ?)", (executed_at_date, migration_name))

        # Commit changes and close the connection
        conn.commit()
        conn.close()

    def add_transaction(self, transaction):
        """Add a transaction to the database."""
        engine = create_engine(f'sqlite:///{db_file}')
        session = sessionmaker(bind=engine)
        session = Session()
        session.add(transaction)
        session.commit()
        session.close()

    def get_transactions(self):
        """Retrieve all transactions from the database."""
        engine = create_engine(f'sqlite:///{db_file}')
        Session = sessionmaker(bind=engine)
        session = Session()
        transactions = session.query(Transaction).all()
        session.close()
        return transactions

    def update_transaction(self, transaction_id, new_transaction_data):
        """Update a transaction in the database."""
        engine = create_engine(f'sqlite:///{db_file}')
        Session = sessionmaker(bind=engine)
        session = Session()
        transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
        for key, value in new_transaction_data.items():
            setattr(transaction, key, value)
        session.commit()
        session.close()

    def delete_transaction(self, transaction_id):
        """Delete a transaction from the database."""
        conn = sqlite3.connect(self.db_file)
        session = conn.cursor()
        transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
        session.delete(transaction)
        conn.commit()
        conn.close()

    def process_convert(self, row, session):
        """Process Convert (To) transaction."""
        timestamp = row['Timestamp']
        asset = row['Asset']
        value = float(row['Total (inclusive of fees and/or spread)'])
        fees = float(row['Fees and/or Spread'])
        description = row['Notes']
        amount = float(description.split()[-2])

        # Get the asset being converted to
        converted_to_asset = description.split()[-1]

        # Calculate new values based on fees
        # if fees >= 0:
        asset_transaction_value = value - fees
        asset_unit_price = asset_transaction_value / amount
        # else:
            # asset_transaction_value = value
            # asset_unit_price = value / amount

        transaction_ts = datetime.strptime(timestamp, self.TIME_FORMAT)

        transaction = Transaction(transaction_ts=transaction_ts, transaction_type=TransactionType.CONVERT_TO.value, asset=converted_to_asset, amount=amount, asset_transaction_value=asset_transaction_value, asset_unit_price=asset_unit_price, fees=0, description=description)
        session.add(transaction)

    def process_transaction_and_insert(self, row, session):
        """Process a transaction row and insert it into the database."""
        transaction_type = row['Transaction Type']
        timestamp = row['Timestamp']
        asset = row['Asset']
        amount = float(row['Quantity Transacted'])
        value = float(row['Total (inclusive of fees and/or spread)'])
        fees = float(row['Fees and/or Spread'])
        description = row['Notes']
        asset_unit_price = value / amount


        if transaction_type == 'Convert':
            self.process_convert(row, session)
            transaction_type = TransactionType.CONVERT_FROM.value
        elif transaction_type == 'Buy':
            transaction_type = TransactionType.BUY.value
        elif transaction_type == 'Receive':
            transaction_type = TransactionType.RECEIVE.value
        elif transaction_type == 'Sell':
            transaction_type = TransactionType.SELL.value
        elif transaction_type == 'Send':
            transaction_type = TransactionType.SEND.value
        elif transaction_type == 'Staking Income':
            transaction_type = TransactionType.STAKING_INCOME.value
        elif transaction_type == 'Unwrap':
            transaction_type = TransactionType.UNWRAP.value
        else:
            print("ERROR: Invalid transaction type")

        transaction_ts = datetime.strptime(timestamp, self.TIME_FORMAT)
        transaction = Transaction(transaction_ts=transaction_ts, transaction_type=transaction_type, asset=asset, amount=amount, asset_transaction_value=value, asset_unit_price=asset_unit_price,fees=fees, description=description)
        session.add(transaction)

    def read_csv_and_insert_to_db(self, csv_file):
        """Read CSV file and insert data into the database."""
        engine = create_engine(f'sqlite:///{db_file}')
        Session = sessionmaker(bind=engine)
        session = Session()

        with open(csv_file, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                self.process_transaction_and_insert(row, session)

        session.commit()
        session.close()



    def get_distinct_assets(self, session):
        """Fetch all distinct assets from the database."""
        distinct_assets = session.query(func.distinct(Transaction.asset)).all()
        return [asset[0] for asset in distinct_assets]

    def get_transactions_for_asset(self, session, asset):
        """Fetch all transactions for a given asset sorted by transaction_ts in ascending order."""
        transactions = session.query(Transaction).filter_by(asset=asset).order_by(Transaction.transaction_ts.asc()).all()
        return transactions

    def set_account_values(self):
        """Fetch all transactions for each distinct asset."""
        engine = create_engine(f'sqlite:///{db_file}')
        Session = sessionmaker(bind=engine)
        session = Session()

        distinct_assets = self.get_distinct_assets(session)

        for asset in distinct_assets:
            starting_balance = 0
            ending_balance=0
            transactions = self.get_transactions_for_asset(session, asset)
            for transaction in transactions:
                transaction.account_starting_balance = starting_balance;

                if (transaction.transaction_type == TransactionType.BUY.value
                        or transaction.transaction_type == TransactionType.CONVERT_TO.value
                        or transaction.transaction_type == TransactionType.RECEIVE.value
                        or transaction.transaction_type == TransactionType.UNWRAP.value
                        or transaction.transaction_type == TransactionType.STAKING_INCOME.value):
                    transaction.account_ending_balance = starting_balance + transaction.amount
                else:
                    transaction.account_ending_balance = starting_balance - transaction.amount

                starting_balance = transaction.account_ending_balance
                session.add(transaction) 
        session.commit()
        session.close() 


if __name__ == '__main__':
    # Example usage
    db_file = 'transactions.sqlite'
    ddl_dir = '../sql'
    csv_file = 'transactions.csv'

    if(os.path.exists(db_file)):
        os.remove(db_file)

    transaction_db = TransactionDatabase(db_file)
    transaction_db.create_database(ddl_dir)
    transaction_db.read_csv_and_insert_to_db(csv_file)
    transaction_db.set_account_values()
