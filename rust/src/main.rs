use chrono::{DateTime, Utc};

pub trait Account<T> {

    fn get_amount(&self) -> f32;
    fn add_transaction(self, transaction: T) -> Result<f32, String> ;
}

#[derive(Clone)]
struct CryptoCurrencyAccount {
    holdings: Vec<Holding>,
    transactions: Vec<Transaction>
}

impl Account<Transaction> for CryptoCurrencyAccount {
    fn get_amount(&self) -> f32{
        let mut sum: f32 = 0.0;
        for holding in self.holdings.iter(){
            sum = sum + holding.amount;
        }

        return sum
    }

    fn add_transaction(mut self, transaction: Transaction) -> Result<f32, String> {

        return Ok(self.get_amount());
    }
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
    price_at_date: f32,
    fee: f32,
    transaction_type: TransactionType,
}

struct Holding {
    date: DateTime<Utc>,
    amount: f32,
    price_at_date: f32,
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


fn main() {
    println!("Hello, world!");
}

#[cfg(test)]
mod crypt_account_unit_test {
    use chrono::{DateTime, Utc};

    use crate::{CryptoCurrencyAccount, Transaction, TransactionType, Account};


    #[test]
    fn single_purchase_transaction(){
        let t = Transaction { date: Utc::now(),
                              amount: 1.0, price_at_date: 43254.23, fee: 2.31, transaction_type: TransactionType::Purchase };

        let mut c = CryptoCurrencyAccount { holdings: vec!(), transactions: vec!() };
        c.add_transaction(t);
        assert_eq!(c.get_amount(), 43254.23) ;

    }


}
