-- Schema
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at DATETIME DEFAULT GETDATE()
);


CREATE TABLE cards (
    card_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    billing_day INT NOT NULL CHECK (billing_day BETWEEN 1 AND 31),
    due_days INT NOT NULL,
    grace_days INT DEFAULT 2,
    credit_limit DECIMAL(10,2),
    card_status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at DATETIME DEFAULT GETDATE(),


    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);


CREATE TABLE transactions (
    txn_id BIGINT PRIMARY KEY,
    card_id INT NOT NULL,
    txn_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    txn_type VARCHAR(50),
    description VARCHAR(255),
    created_ts DATETIME DEFAULT GETDATE(),


    FOREIGN KEY (card_id) REFERENCES cards(card_id)
);


CREATE TABLE bills (
    bill_id BIGINT PRIMARY KEY,
    card_id INT NOT NULL,
   
    billing_start_date DATE NOT NULL,
    billing_end_date DATE NOT NULL,
   
    bill_date DATE NOT NULL,
    due_date DATE NOT NULL,


    total_amount DECIMAL(10,2) NOT NULL,
    minimum_due DECIMAL(10,2) NOT NULL,
    remaining_amount DECIMAL(10,2),


    late_fee DECIMAL(10,2) DEFAULT 0,
    interest DECIMAL(10,2) DEFAULT 0,
    total_charges DECIMAL(10,2) DEFAULT 0,


    bill_status VARCHAR(20) NOT NULL,
   
    created_ts DATETIME DEFAULT GETDATE(),


    FOREIGN KEY (card_id) REFERENCES cards(card_id)
);
ALTER TABLE bills
ADD CONSTRAINT chk_remaining CHECK (remaining_amount >= 0);
ALTER TABLE bills
ADD CONSTRAINT uq_bill UNIQUE (card_id, billing_start_date, billing_end_date); 


CREATE TABLE bill_transactions (
    bill_txn_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    bill_id BIGINT NOT NULL,
    txn_id BIGINT NOT NULL,
    amount DECIMAL(10,2),


    FOREIGN KEY (bill_id) REFERENCES bills(bill_id),
    FOREIGN KEY (txn_id) REFERENCES transactions(txn_id)
);


CREATE TABLE payments (
    payment_id BIGINT PRIMARY KEY,
    card_id INT NOT NULL,
    bill_id BIGINT NOT NULL,
    payment_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),


    payment_status VARCHAR(20),
    txn_reference VARCHAR(100),


    created_ts DATETIME DEFAULT GETDATE(),


    FOREIGN KEY (card_id) REFERENCES cards(card_id),
    FOREIGN KEY (bill_id) REFERENCES bills(bill_id)
);


CREATE TABLE charges (
    charge_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    bill_id BIGINT NOT NULL,
    charge_type VARCHAR(50),  -- late_fee / interest
    amount DECIMAL(10,2),
    applied_date DATE,


    FOREIGN KEY (bill_id) REFERENCES bills(bill_id)
);

CREATE TABLE late_fee_config (
   id INT IDENTITY(1,1) PRIMARY KEY,
   min_amount DECIMAL(10,2),
   max_amount DECIMAL(10,2),
   fee DECIMAL(10,2)
);


CREATE INDEX idx_txn_card_date ON transactions(card_id, txn_date);
CREATE INDEX idx_bill_card ON bills(card_id);
CREATE INDEX idx_payment_bill ON payments(bill_id);
Schema Validation
SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE';


INSERT INTO transactions (txn_id, card_id, txn_date, amount)
VALUES (9999, 999, '2026-04-01', 100);


-- should fail (amount > 0)
INSERT INTO transactions (txn_id, card_id, txn_date, amount)
VALUES (9998, 101, '2026-04-01', -500);


-- should fail
INSERT INTO bills (bill_id, card_id)
VALUES (1, 101);




-- Alter schema for constrains
ALTER TABLE bills
ADD CONSTRAINT uq_bill UNIQUE (card_id, billing_start_date, billing_end_date);


ALTER TABLE bills
ADD CONSTRAINT chk_bill_status
CHECK (bill_status IN ('GENERATED','PAID','MIN_PAID','PARTIAL','OVERDUE'));


ALTER TABLE bills
ADD CONSTRAINT chk_dates
CHECK (billing_start_date < billing_end_date);

-- Improve bill_transactions Constraint
ALTER TABLE bill_transactions
ADD CONSTRAINT uq_bill_txn UNIQUE (bill_id, txn_id);

ALTER TABLE bills
ADD CONSTRAINT chk_amounts CHECK (total_amount >= minimum_due);





-- Insertion of data




-- #  1. Customers




INSERT INTO customers (customer_id, full_name, email) VALUES
(1, 'Rahul Sharma', 'rahul.sharma@gmail.com'),
(2, 'Priya Reddy', 'priya.reddy@gmail.com'),
(3, 'Amit Kumar', 'amit.kumar@gmail.com'),
(4, 'Sneha Patil', 'sneha.patil@gmail.com'),
(5, 'Vikram Singh', 'vikram.singh@gmail.com'),
(6, 'Neha Gupta', 'neha.gupta@gmail.com'),
(7, 'Arjun Mehta', 'arjun.mehta@gmail.com'),
(8, 'Pooja Nair', 'pooja.nair@gmail.com'),
(9, 'Karan Verma', 'karan.verma@gmail.com'),
(10, 'Anjali Das', 'anjali.das@gmail.com');




---


-- #  2. Cards




INSERT INTO cards
(card_id, customer_id, billing_day, due_days, grace_days, credit_limit, card_status)
VALUES
(101, 1, 1, 20, 2, 50000, 'ACTIVE'),
(102, 2, 5, 18, 2, 60000, 'ACTIVE'),
(103, 3, 10, 20, 2, 45000, 'ACTIVE'),
(104, 4, 12, 15, 2, 40000, 'ACTIVE'),
(105, 5, 15, 20, 2, 70000, 'ACTIVE'),
(106, 6, 18, 22, 2, 55000, 'ACTIVE'),
(107, 7, 20, 18, 2, 50000, 'ACTIVE'),
(108, 8, 22, 20, 2, 48000, 'ACTIVE'),
(109, 9, 25, 15, 2, 65000, 'ACTIVE'),
(110, 10, 28, 20, 2, 30000, 'ACTIVE');


--  3. Transactions




INSERT INTO transactions
(txn_id, card_id, txn_date, amount, txn_type, description)
VALUES


-- Rahul
(1001, 101, '2026-03-02', 2500, 'shopping', 'Amazon'),
(1002, 101, '2026-03-10', 1200, 'food', 'Swiggy'),
(1003, 101, '2026-03-15', 5000, 'electronics', 'Croma'),
(1004, 101, '2026-03-25', 2000, 'fuel', 'Indian Oil'),


-- Priya
(1005, 102, '2026-03-06', 3000, 'shopping', 'Flipkart'),
(1006, 102, '2026-03-12', 800, 'food', 'Zomato'),
(1007, 102, '2026-03-20', 10000, 'travel', 'Flight'),


-- Amit
(1008, 103, '2026-03-11', 1500, 'grocery', 'Reliance'),
(1009, 103, '2026-03-18', 7000, 'electronics', 'Vijay Sales'),
(1010, 103, '2026-03-25', 2000, 'fuel', 'HP Petrol'),


-- Sneha
(1011, 104, '2026-03-13', 2500, 'shopping', 'Myntra'),
(1012, 104, '2026-03-20', 1200, 'food', 'Swiggy'),


-- Vikram
(1013, 105, '2026-03-16', 8000, 'electronics', 'Samsung'),
(1014, 105, '2026-03-22', 3000, 'cash_withdrawal', 'ATM'),


-- Neha
(1015, 106, '2026-03-19', 4000, 'shopping', 'Ajio'),
(1016, 106, '2026-03-25', 1500, 'food', 'Zomato'),


-- Arjun
(1017, 107, '2026-03-21', 6000, 'travel', 'Train'),
(1018, 107, '2026-03-28', 2000, 'fuel', 'BPCL'),


-- Pooja
(1019, 108, '2026-03-23', 3500, 'shopping', 'Nykaa'),
(1020, 108, '2026-03-27', 1000, 'food', 'Swiggy'),


-- Karan
(1021, 109, '2026-03-26', 9000, 'electronics', 'Laptop'),


-- Anjali
(1022, 110, '2026-03-29', 2000, 'shopping', 'Flipkart'),
(1023, 110, '2026-03-30', 500, 'food', 'Zomato');

-- ✅ Insert Slabs
INSERT INTO late_fee_config (min_amount, max_amount, fee) VALUES
(0, 100, 0),
(100, 500, 100),
(500, 1000, 500),
(1000, 10000, 750),
(10000, 25000, 950),
(25000, 50000, 1100),
(50000, NULL, 1300);



/*
--  4.  Payments (DEFERRED)


👉 **Do NOT insert yet**


Reason:


* `bill_id` comes from billing engine
* FK will fail


---


## ✅ When to insert payments?


👉 AFTER bill generation


---*/
/*
## 🔹 Future Payments Template (Keep Ready)


```sql
INSERT INTO payments
(payment_id, card_id, bill_id, payment_date, amount, payment_status, txn_reference)
VALUES
(2001, 101, 5001, '2026-04-18', 10700, 'SUCCESS', 'TXN001');
```


---


#  🧪 5. Final Validation Queries


Run these:


---


### ✔ Check Data Loaded*/




SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM cards;
SELECT COUNT(*) FROM transactions;

-- Join Validation

SELECT
    c.full_name,
    ca.card_id,
    t.txn_id,
    t.amount
FROM customers c
JOIN cards ca ON c.customer_id = ca.customer_id
JOIN transactions t ON ca.card_id = t.card_id;






-/*FINAL STATUS


| Component    | Status             |
| ------------ | ------------------ |
| Customers    | ✅ Ready            |
| Cards        | ✅ Ready            |
| Transactions | ✅ Ready            |
| Payments     | ⏳ Wait for billing |




