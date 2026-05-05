# Databricks notebook source
# MAGIC %md
# MAGIC ### INSERT INTO BILL and TRANSACTION TABLE 

# COMMAND ----------

# MAGIC %md
# MAGIC install reportlab and restart cluster to generate pdf.

# COMMAND ----------

# MAGIC %pip install reportlab
# MAGIC

# COMMAND ----------

# MAGIC %restart_python 

# COMMAND ----------

# MAGIC %md
# MAGIC STORAGE ACCOUNT DETAILS

# COMMAND ----------

storage_account = "stccbillingdata"
access_key = "6EiS1CNIxAK/H54mW3RLm5+f7Z5aNj7nWpfuoDLrSRE7F+arnl9ZfhTI7ytdULonZ0Flb15Za5zM+ASt/+Ldtg=="

spark.conf.set(
    f"fs.azure.account.key.{storage_account}.dfs.core.windows.net",
    access_key
)


# COMMAND ----------

# MAGIC %md
# MAGIC FILE PATH CREATION

# COMMAND ----------

from datetime import datetime

# today = datetime.now().strftime("%Y%m%d")
today=20260504
print(today)  # e.g. 20260504
base_path = "abfss://billing@stccbillingdata.dfs.core.windows.net"

customers_path = f"{base_path}/customers/{today}/billing_customers_{today}.parquet"
cards_path = f"{base_path}/cards/{today}/billing_cards_{today}.parquet"
transactions_path = f"{base_path}/transactions/{today}/billing_transactions_{today}.parquet"

print(customers_path)
print(cards_path)
print(transactions_path)

# COMMAND ----------

# MAGIC %md
# MAGIC DATAFRAMES CREATION FOR THE FILES

# COMMAND ----------

customers_df = spark.read.parquet(customers_path)
cards_df = spark.read.parquet(cards_path)
txn_df = spark.read.parquet(transactions_path)


# COMMAND ----------

# DBTITLE 1,Cell 4
# MAGIC %skip
# MAGIC display(customers_df)
# MAGIC display(cards_df)
# MAGIC display(txn_df)

# COMMAND ----------

# MAGIC %md
# MAGIC BILL TABLE DATA GENERATION USING CARDS, CUSTOMERS, AND TRANSACTION FILES EXTRACTED FOR TOYDA BILL DATE

# COMMAND ----------

from pyspark.sql.functions import dayofmonth, current_date

cards_today_df = cards_df.filter(
    dayofmonth(current_date()) == cards_df.billing_day
)

# display(cards_today_df)


# COMMAND ----------

from pyspark.sql.functions import add_months, col

cards_today_df = cards_today_df.withColumn(
    "billing_end_date", current_date()
).withColumn(
    "billing_start_date",
    add_months(col("billing_end_date"), -1)
)

# display(cards_today_df)


# COMMAND ----------

txn_filtered_df = txn_df.join(
    cards_today_df.select("card_id", "billing_start_date", "billing_end_date"),
    "card_id"
).filter(
    (col("txn_date") >= col("billing_start_date")) &
    (col("txn_date") <= col("billing_end_date"))
)

# display(txn_filtered_df)

# COMMAND ----------

from pyspark.sql.functions import when

txn_filtered_df = txn_filtered_df.withColumn(
    "cash_fee",
    when(col("txn_type") == "cash_withdrawal", col("amount") * 0.02).otherwise(0)
)

# display(txn_filtered_df)

# COMMAND ----------

from pyspark.sql.functions import sum

bill_calc_df = txn_filtered_df.groupBy("card_id").agg(
    sum("amount").alias("total_amount"),
    sum("cash_fee").alias("cash_fee_total")
)

# display(bill_calc_df)

# COMMAND ----------

from pyspark.sql.functions import when

bill_calc_df = bill_calc_df.withColumn(
    "minimum_due",
    when(col("total_amount") * 0.05 > 200, col("total_amount") * 0.05)
    .otherwise(200)
)

# display(bill_calc_df)

# COMMAND ----------

from pyspark.sql.functions import date_add

bill_calc_df = bill_calc_df.join(cards_today_df, "card_id")

bill_calc_df = bill_calc_df.withColumn(
    "bill_date", col("billing_end_date")
).withColumn(
    "due_date",
    date_add(col("bill_date"), col("due_days"))
)

# display(bill_calc_df)


# COMMAND ----------

from pyspark.sql.functions import lit

bill_final_df = bill_calc_df.withColumn(
    "remaining_amount", col("total_amount")
).withColumn(
    "late_fee", lit(0)
).withColumn(
    "interest", lit(0)
).withColumn(
    "total_charges", col("cash_fee_total")
).withColumn(
    "bill_status", lit("GENERATED")
).select(
    "card_id",
    "billing_start_date",
    "billing_end_date",
    "bill_date",
    "due_date",
    "total_amount",
    "minimum_due",
    "remaining_amount",
    "late_fee",
    "interest",
    "total_charges",
    "bill_status"
)
# display(bill_final_df)


# COMMAND ----------

from pyspark.sql.types import DecimalType

bill_final_df = bill_final_df \
    .withColumn("total_amount", col("total_amount").cast(DecimalType(10,2))) \
    .withColumn("minimum_due", col("minimum_due").cast(DecimalType(10,2))) \
    .withColumn("remaining_amount", col("remaining_amount").cast(DecimalType(10,2))) \
    .withColumn("late_fee", col("late_fee").cast(DecimalType(10,2))) \
    .withColumn("interest", col("interest").cast(DecimalType(10,2))) \
    .withColumn("total_charges", col("total_charges").cast(DecimalType(10,2)))

# COMMAND ----------

bill_final_df = bill_final_df.select(
    "card_id",
    "billing_start_date",
    "billing_end_date",
    "bill_date",
    "due_date",
    "total_amount",
    "minimum_due",
    "remaining_amount",
    "late_fee",
    "interest",
    "total_charges",
    "bill_status"
)

# display(bill_final_df)


# COMMAND ----------

# MAGIC %md
# MAGIC MICROSOFT ENTRA ID AUTHENTICATION WITH AZURE SQL USING CLIENT SECRET

# COMMAND ----------

import requests

tenant_id = "4c5bf625-716b-491d-8147-cfbd66b4bc7f"
client_id = "ae31d9fe-b85f-4689-88a8-0d538e107ba4"
client_secret = "knh8Q~IpYg.XH6ShkKtADzRDb3sSTRvxFIMGqa-F"



url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"

payload = {
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret,
    "resource": "https://database.windows.net/"
}

response = requests.post(url, data=payload)
json_response = response.json()
access_token = json_response.get("access_token") if json_response else None



# COMMAND ----------

# import base64
# import json

# payload = access_token.split('.')[1]
# decoded = json.loads(base64.b64decode(payload + '=='))

# # print(decoded["tid"])   # tenant id inside token
# # print(decoded["appid"]) # client id inside token

# COMMAND ----------

JDBC FOR CONNECTION BETWEEN DATABRICKS AND AZURE SQL 

# COMMAND ----------

jdbc_url = "jdbc:sqlserver://abdc-billing-sql-server.database.windows.net:1433;database=Creditcard_billing_db;encrypt=true;"
connection_properties = {
    "accessToken": access_token,
    "driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver"
}

# COMMAND ----------

# MAGIC %md
# MAGIC WRITE BILL DATAFRAME TO BILL TABLE
# MAGIC BILL ID WILL BE GENERATED IN SQL. 

# COMMAND ----------

bill_final_df.write.jdbc(
    url=jdbc_url,
    table="bills",
    mode="append",
    properties={
        "accessToken": access_token,
        "driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver"
    }
)

# COMMAND ----------

# MAGIC %md
# MAGIC READ BILL DATA FROM SQL WITH BILL ID TO WIRTE TRANSACTION TABLE

# COMMAND ----------

bills_sql_df = spark.read.jdbc(
    url=jdbc_url,
    table="bills",
    properties={
        "accessToken": access_token,
        "driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver"
    }
)

# COMMAND ----------

bill_with_id_df = bills_sql_df.join(
    bill_final_df,
    on=["card_id", "billing_start_date", "billing_end_date"],
    how="inner"
).select(
    "bill_id",
    "card_id"
)

bill_txn_df = txn_filtered_df.join(
    bill_with_id_df,
    "card_id"
).select(
    "bill_id",
    "txn_id",
    "amount"
)

# COMMAND ----------

# MAGIC %md
# MAGIC WRITE INTO BILL TRANSACTION TABLE 

# COMMAND ----------

bill_txn_df.write.jdbc(
    url=jdbc_url,
    table="bill_transactions",
    mode="append",
    properties=connection_properties
)

# COMMAND ----------

bill_with_id_df = bill_final_df.join(
    bills_sql_df,
    on=[
        "card_id",
        "billing_start_date",
        "billing_end_date"
    ],
    how="inner"
).select(
    bills_sql_df.bill_id,
    bill_final_df.card_id,
    bill_final_df.billing_start_date,
    bill_final_df.billing_end_date
)

# COMMAND ----------

# MAGIC %md
# MAGIC # BILL GENERATION

# COMMAND ----------

from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from azure.storage.blob import BlobServiceClient

# COMMAND ----------

# MAGIC %md
# MAGIC PDF CREATION

# COMMAND ----------

def generate_bill_pdf(row, txn_list, customer):

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # ================= HEADER =================
    c.setFont("Helvetica-Bold", 16)
    c.drawString(180, 800, "CREDIT CARD STATEMENT")

    # ================= CUSTOMER INFO =================
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, 770, "CUSTOMER DETAILS")

    c.setFont("Helvetica", 10)
    c.drawString(50, 755, f"Name: {customer.get('full_name', 'N/A')}")
    c.drawString(50, 740, f"Email: {customer.get('email', 'N/A')}")
    c.drawString(50, 725, f"Customer ID: {customer.get('customer_id', 'N/A')}")
    c.drawString(50, 710, f"Mobile: {customer.get('mobile', 'N/A')}")

    # ================= CARD INFO =================
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, 685, "CARD DETAILS")

    c.setFont("Helvetica", 10)
    c.drawString(50, 670, f"Card ID: {row['card_id']}")
    c.drawString(50, 655, f"Bill Date: {row['bill_date']}")
    c.drawString(50, 640, f"Due Date: {row['due_date']}")

    # ================= BILL SUMMARY =================
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, 615, "BILL SUMMARY")

    c.setFont("Helvetica", 10)
    c.drawString(50, 600, f"Total Amount: {row['total_amount']}")
    c.drawString(50, 585, f"Minimum Due: {row['minimum_due']}")
    c.drawString(50, 570, f"Late Fee: {row['late_fee']}")
    c.drawString(50, 555, f"Total Charges: {row['total_charges']}")
    c.drawString(50, 540, f"Remaining: {row['remaining_amount']}")

    # ================= TRANSACTIONS =================
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, 510, "TRANSACTIONS")

    c.setFont("Helvetica", 9)
    y = 490

    for txn in txn_list:
        line = f"{txn['txn_id']} | {txn.get('txn_type','NA')} | {txn['amount']}"
        c.drawString(50, y, line)
        y -= 15

        if y < 80:
            c.showPage()
            y = 750

    c.save()

    buffer.seek(0)
    return buffer


# COMMAND ----------

# MAGIC %md
# MAGIC BLOB SERVICES CONNECTION FOR STORING  GENERATED  BILLS IN ADLS

# COMMAND ----------

conn_str = "DefaultEndpointsProtocol=https;AccountName=stccbillingdata;AccountKey=6EiS1CNIxAK/H54mW3RLm5+f7Z5aNj7nWpfuoDLrSRE7F+arnl9ZfhTI7ytdULonZ0Flb15Za5zM+ASt/+Ldtg==;EndpointSuffix=core.windows.net"
blob_service = BlobServiceClient.from_connection_string(conn_str)

# COMMAND ----------

STORING BILLS IN ADLS

# COMMAND ----------

# =========================
# 1. READ BILLS FROM SQL
# =========================
bills = spark.read.jdbc(
    jdbc_url,
    "bills",
    properties=connection_properties
).collect()


# =========================
# 2. LOOP THROUGH EACH BILL
# =========================
for b in bills:

    # -------------------------
    # GET TRANSACTIONS FOR BILL
    # -------------------------
    txn_list = spark.read.jdbc(
        jdbc_url,
        "bill_transactions",
        properties=connection_properties
    ).filter(
        f"bill_id = {b.bill_id}"
    ).collect()

    # -------------------------
    # GET CUSTOMER DETAILS
    # -------------------------
    card_row = spark.read.jdbc(
        jdbc_url,
        "cards",
        properties=connection_properties
    ).filter(
        f"card_id = {b.card_id}"
    ).collect()[0]

    customer_row = spark.read.jdbc(
        jdbc_url,
        "customers",
        properties=connection_properties
    ).filter(
        f"customer_id = {card_row.customer_id}"
    ).collect()[0]


    customer = customer_row.asDict()

    # -------------------------
    # GENERATE PDF + UPLOAD
    # -------------------------
    pdf_buffer = generate_bill_pdf(
        b.asDict(),
        [t.asDict() for t in txn_list],
        customer
    )

    blob_path = f"pdfs/bill_{b.bill_id}_{b.card_id}.pdf"

    blob_client = blob_service.get_blob_client(
        container="billing",
        blob=blob_path
    )

    blob_client.upload_blob(pdf_buffer, overwrite=True)

    print("Generated:", blob_path)