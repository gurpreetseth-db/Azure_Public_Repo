# Databricks notebook source
# MAGIC %md <a href='$../Azure Integrations Start Here'>Home</a>

# COMMAND ----------

# MAGIC %md
# MAGIC # Azure SQL Using Spark JDBC Connector

# COMMAND ----------

# MAGIC %md
# MAGIC ### Note
# MAGIC ## At presnet com.microsoft.azure:spark-mssql-connector_2.12:1.2.0 is not compliant with Spark 3.3.0 hence need to use LTS 10.4
# MAGIC ## Also, please make sure that you added you IP Addresses under Firewall rule in SQL Server
# MAGIC 1. Go to SQL Server <3CHAR>-001-sqlserver
# MAGIC 2. Left side, under Security -> Networking
# MAGIC 3. Firewall Rules, Add you client IPv4 address (xxxx.xxx.xxx.xxx)

# COMMAND ----------

keyvault_secret_scope = "Databricks-KeyVault-Scope" # The Azure Key Vault Secret Scope
keyvault_sqldbatabase_username = "sqlserver-db-user" 
keyvault_sqldbatabase_password = "sqlserver-db-password" 
keyvault_sqldatabase_url = "sqlserver-jdbc-connection-string"

username = dbutils.secrets.get(scope = keyvault_secret_scope, key = keyvault_sqldbatabase_username) 
password = dbutils.secrets.get(scope = keyvault_secret_scope, key = keyvault_sqldbatabase_password) 
url = dbutils.secrets.get(scope = keyvault_secret_scope, key = keyvault_sqldatabase_url) 

table_name = 'dbo.Capitals'


# COMMAND ----------

# Sample DataSet
from pyspark.sql.types import StructType,StructField, StringType, IntegerType

data2 =  [("Canberra","Australia",2000000),
         ("London","United Kingdom",8900000),
         ("Washington","United States Of America",7500000),
         ("Tokyo","Japan",1300000)
         ]

schema = StructType([ \
    StructField("city",StringType(),True), \
    StructField("country",StringType(),True), \
    StructField("population", IntegerType(), True) \
  ])


df = spark.createDataFrame(data=data2,schema=schema)
df.printSchema()
df.show(truncate=False)

# COMMAND ----------

df.write \
    .format("com.microsoft.sqlserver.jdbc.spark") \
    .mode("overwrite") \
    .option("url", url) \
    .option("dbtable", table_name) \
    .option("user", username) \
    .option("password", password) \
    .save()



# COMMAND ----------

asqlDF = spark.read \
        .format("com.microsoft.sqlserver.jdbc.spark") \
        .option("url", url) \
        .option("dbtable", table_name) \
        .option("user", username) \
        .option("password", password).load()

# COMMAND ----------

display(asqlDF)

# COMMAND ----------

# MAGIC %md
# MAGIC **INSERT into Table**

# COMMAND ----------

# Sample DataSet
from pyspark.sql.types import StructType,StructField, StringType, IntegerType

data2 =  [("Melbourne","Australia",5070000),
         ("sydney","Australia",5312000)]

schema = StructType([ \
    StructField("city",StringType(),True), \
    StructField("country",StringType(),True), \
    StructField("population", IntegerType(), True) \
  ])
 

# COMMAND ----------

df2 = spark.createDataFrame(data=data2,schema=schema)
df2.printSchema()
df2.show(truncate=False)


# COMMAND ----------

try:
  df2.write \
    .format("com.microsoft.sqlserver.jdbc.spark") \
    .mode("append") \
    .option("url", url) \
    .option("dbtable", table_name) \
    .option("user", username) \
    .option("password", password) \
    .save()
except ValueError as error :
    print("Connector write failed", error)

# COMMAND ----------

asqlDF = spark.read \
        .format("com.microsoft.sqlserver.jdbc.spark") \
        .option("url", url) \
        .option("dbtable", table_name) \
        .option("user", username) \
        .option("password", password).load()

# COMMAND ----------

display(asqlDF)
