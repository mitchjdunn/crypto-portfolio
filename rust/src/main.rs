use chrono::{DateTime, Utc};

fn main() {
    println!("Hello, world!");
}

#[derive(Copy, Clone)]
enum TransactionType {
    Purchase,
    Sale,
}

#[derive(Copy, Clone)]
struct Transaction {
    date: DateTime<Utc>,
    amount: f32,
    price_at_datypete: f32,
    fee: f32,
    transaction_type: TransactionType,
}

struct Holding {
    date: DateTime<Utc>,
    amount: f32,
    priceAtDate: f32,
    history: Vec<Transaction>,
}

impl Holding {
    pub fn add_transaction(mut self, transaction: Transaction) -> Result<f32, String> {

        if self.amount - transaction.amount < 0.0 {
            return Err("This will drop transaction below 0".to_string());
        }

        self.history.push(transaction);
        self.amount = self.amount - transaction.amount;

        return Ok(self.amount);
    }
}

struct CryptoCurrencyHolding {
    holdings: Vec<Holding>,
    transactions: Vec<Transaction>
}

impl CryptoCurrencyHolding {
    fn get_total(&self) -> f32{
        let mut sum: f32 = 0.0;
        for holding in self.holdings.iter(){
            sum = sum + holding.amount;
        }

        return sum
    }

    fn add_transaction(mut self, transaction: Transaction) -> Result<f32, String> {

        match transaction.transaction_type {
            TransactionType::Purchase => {
                self.transactions.append(transaction);
                self.holdings.append(new Holding())
            },
            TransactionType::Sale => {
                // TODO Subtract from holding
                // TODO get a rule set injected here
            },
        }


        return Ok(self.get_total());
    }
}
