# 💳 Credit Card Billing System (Azure Data Engineering Project)

## 📌 Overview
This project implements an end-to-end credit card billing system using Azure services. It simulates real-world banking workflows such as transaction processing, bill generation, PDF statement creation, and automated email delivery.

---

## 🏗️ Architecture
![Architecture](docs/architecture_diagram.png)

---

## ⚙️ Tech Stack
- Azure Data Factory (ADF)
- Azure Databricks (PySpark)
- Azure Data Lake Storage (ADLS Gen2)
- Azure SQL Database
- Azure Logic Apps
- ReportLab (PDF Generation)

---

## 🔄 Workflow

1. Extract data from Azure SQL → ADLS (Parquet)
2. Process billing logic in Databricks
3. Store bills in Azure SQL
4. Map transactions to bills
5. Generate PDF statements
6. Store PDFs in ADLS
7. Send emails using Logic Apps

---

## 🧠 Business Logic

- Billing cycle based on billing_day
- Minimum due = max(5% of total, 200)
- Cash withdrawal fee = 2%
- Due date = bill_date + due_days

---

## 📂 Project Structure

- notebooks/ → PySpark processing
- sql/ → schema & configurations
- adf/ → pipeline JSON
- logic_app/ → email workflow
- docs/ → documentation & diagrams

---

## 🚀 How to Run

1. Upload data to Azure SQL
2. Run ADF pipeline
3. Execute Databricks notebooks
4. Trigger Logic App for email delivery

---

## ⚠️ Challenges Solved

- Data type mismatch (nvarchar → bigint)
- bill_id generation issues
- DBFS file system errors
- PDF generation failures
- ADF & Logic App integration issues

---

## 🔮 Future Enhancements

- Payment system
- Late fee automation
- Power BI dashboard
- Fraud detection

---

## 👤 Author
Chanikya Ladi
