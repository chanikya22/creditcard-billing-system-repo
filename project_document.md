End-to-End Credit Card Billing System on Azure
Author
Chanikya Ladi
Target Role: Data Engineer
google Docs link:
https://docs.google.com/document/d/1LI-BV59mFjhpunSYTHWtQ6mrB2438TObftrJHEykVOA/edit?pli=1&tab=t.kavagabhxnns#heading=h.j16hfqpyiuq9
________________________________________
1. Abstract
This project implements a complete credit card billing system using Azure data engineering tools. It simulates real-world banking workflows including transaction processing, monthly bill generation, PDF statement creation, and automated email delivery.
The system is designed to be scalable, modular, and production-ready.
________________________________________
2. Architecture Diagram
        +----------------------+
        |  Azure SQL (Source)  |
        +----------+-----------+
                   |
                   v
        +----------------------+
        | Azure Data Factory   |
        | (Data Extraction)    |  
        +----------+-----------+
                   |
                   v
        +----------------------+
        | ADLS Gen2 (Parquet)  |
        +----------+-----------+
                   |
                   v
        +----------------------+
        | Databricks (PySpark) |
        | Billing Engine       |
        +----------+-----------+
                   |
                   v
        +----------------------+
        | Azure SQL (Bills DB) |
        +----------+-----------+
                   |
         +---------+---------+
         |                   |
         v                   v
+----------------+   +----------------------+
| bill_transactions|   | PDF Generation       |
| table           |   | (ReportLab)          |
+--------+-------+   +----------+-----------+
         |                      |
         v                      v
   +-------------------------------+
   | ADLS (PDF Storage)            |
   +---------------+---------------+
                   |
                   v
        +----------------------+
        | Azure Data Factory   |
        | (Trigger Email Flow) |
        +----------+-----------+
                   |
                   v
        +----------------------+
        | Azure Logic Apps     |
        | Email Service        |
        +----------+-----------+
                   |
                   v
        +----------------------+
        | Customer Email       |
        +----------------------+
________________________________________
3. Tech Stack
•	Databricks (PySpark)
•	Azure SQL Database
•	Azure Data Lake Storage (ADLS Gen2)
•	Azure Data Factory (ADF)
•	Azure Logic Apps
•	ReportLab (PDF Generation)
•	Python, SQL
________________________________________
4. Data Model
Tables Used
•	customers
•	cards
•	transactions
•	bills
•	bill_transactions
•	payments (planned)
•	charges (planned)
•	late_fee_config
Relationships
customers → cards → transactions
cards → bills → bill_transactions
bills → payments → charges
________________________________________
5. Pipeline Flow
Step 1: Data Extraction
•	Source: Azure SQL
•	Tool: ADF
•	Target: ADLS (Parquet files)
Step 2: Billing Engine (Databricks)
•	Filter cards based on billing_day
•	Filter transactions within billing period
•	Aggregate transactions
Step 3: Bill Calculation
•	total_amount = sum(transactions)
•	minimum_due = max(5% of total, 200)
•	cash withdrawal fee = 2%
•	due_date = bill_date + due_days
Step 4: Store Bills
•	Insert into bills table
•	Fetch generated bill_id
Step 5: Transaction Mapping
•	Map transactions to bill_id
•	Insert into bill_transactions
Step 6: PDF Generation
•	Generate PDF using ReportLab
•	Include customer, card, bill, and transaction details
•	Store in ADLS: billing/pdfs/bill__.pdf
Step 7: Email Delivery
•	ADF triggers Logic App
•	Logic App reads PDF from ADLS
•	Sends email to customer
________________________________________
6. Business Logic
•	Monthly billing cycle based on billing_day
•	Minimum due = max(5% of total_amount, 200)
•	Cash withdrawal fee = 2%
•	Due date = bill_date + due_days
Late Fee Logic (Designed)
•	Slab-based late fee using late_fee_config
•	Grace period applied
•	Interest logic planned
________________________________________
7. Challenges and Solutions
1. Data Type Issues
•	Problem: nvarchar to bigint errors
•	Solution: Explicit casting in PySpark
2. bill_id Handling
•	Problem: ID mismatch
•	Solution: Let SQL generate and re-fetch
3. File System Errors
•	Problem: Cannot use /tmp or /dbfs
•	Solution: Write directly to ADLS
4. PDF Generation Issues
•	Problem: File write failures
•	Solution: Use in-memory buffer (BytesIO)
5. ADF Integration Errors
•	Problem: Blob path not found
•	Solution: Correct container and path separation
6. dbutils Error
•	Problem: Not usable in distributed jobs
•	Solution: Avoid using inside Spark transformations
________________________________________
8. Scalability
•	Tested on small dataset (~100 rows)
•	Designed for large-scale processing
•	Uses distributed computing with PySpark
________________________________________
9. Future Enhancements
•	Payment processing system
•	Late fee automation
•	Interest calculation engine
•	Power BI dashboard
•	Real-time data processing
•	Fraud detection system
________________________________________
10. Notes (For Future Updates)
(Add new features, improvements, or modules here as you develop further)
________________________________________
11. Conclusion
This project demonstrates a complete real-world data engineering pipeline covering data ingestion, transformation, storage, and delivery. It highlights strong understanding of Azure ecosystem and distributed data processing.
________________________________________
(End of Document)

 
