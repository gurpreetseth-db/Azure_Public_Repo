# Databricks notebook source
# MAGIC %md <a href='$../Azure Integrations Start Here'>Home</a>

# COMMAND ----------

# MAGIC %md
# MAGIC <img src="https://jokdemoresourcessa.blob.core.windows.net/images/azure_newDB_color_transp.png" alt="Azure Databricks" width="600">
# MAGIC <img src="https://jokdemoresourcessa.blob.core.windows.net/images/AzureSynapseAnalytics.png" alt="Azure Synapse Analytics" width="100">
# MAGIC # Azure Synapse Integration

# COMMAND ----------

# MAGIC %md
# MAGIC ### Setup connection string to SQL DW (JDBC)

# COMMAND ----------

# Super secret information! - Azure credential information and connection string parameters
keyvault_secret_scope = "Databricks-KeyVault-Scope" 
keyvault_sql_user = "synapse-db-user" 
keyvault_sql_password = "synapse-db-password"
keyvault_synapse_url = "synapse-jdbc-connection-string"
keyvault_storage_account = "storage-account-name"
keyvault_storage_access_key = "storage-access-key"


username = dbutils.secrets.get(scope = keyvault_secret_scope, key = keyvault_sql_user)
password = dbutils.secrets.get(scope = keyvault_secret_scope, key = keyvault_sql_password)
conn_url =  dbutils.secrets.get(scope = keyvault_secret_scope, key = keyvault_synapse_url)
storage_account =  dbutils.secrets.get(scope = keyvault_secret_scope, key = keyvault_storage_account)
storage_access_key =  dbutils.secrets.get(scope = keyvault_secret_scope, key = keyvault_storage_access_key)

adlscontainer = 'synapse'



# COMMAND ----------

# Extract Synapse workspace name to add in connection string next 
import re

connection_string = conn_url

match = re.search(r'//(.*?).sql', connection_string)

if match:
    extracted_string = match.group(1)
else:
    print("No match found.")

# COMMAND ----------

# Setup some connection parameters
conn_string = conn_url+'user='+username+'@'+extracted_string+';password='+password+';encrypt=true;trustServerCertificate=false;hostNameInCertificate=*.sql.azuresynapse.net;loginTimeout=30;'

#spark conf to use this later in SQL connection
spark.conf.set("synapse.conn_string",conn_string)
spark.conf.set("adls.accountname",storage_account)

spark.conf.set(
  'fs.azure.account.key.'+storage_account+'.blob.core.windows.net',
  storage_access_key)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Create a new table in SQL DW from a Spark Dataframe

# COMMAND ----------

from pyspark.sql.types import IntegerType, StructType, StructField, StringType
from pyspark.sql import Row
from decimal import Decimal

airlinesSchema = StructType(
  [
    StructField('Name', StringType()),
    StructField('Country', StringType()),
    StructField('age', IntegerType())
  ]
)

dfAirlines = spark.createDataFrame(
  [
    Row("American Airlines", "USA", 84),
    Row("British Airways", "UK", 46),
    Row("Japan Airlines", "Japan", 69),
    Row("Singapore Airlines", "Singapore", 47),
    Row("QANTAS", "Australia", 100)
  ], airlinesSchema
)

display(dfAirlines)

# COMMAND ----------

# MAGIC %md
# MAGIC #### By using ADLSg2 as the temporary storage container, we can use the T-SQL COPY command to transfer data from Databricks to Synapse DW much more quickly. This is enabled by default on Databricks Runtime 7.*

# COMMAND ----------

spark.conf.set(
  'fs.azure.account.key.'+storage_account+'.dfs.core.windows.net',
  storage_access_key
)

# COMMAND ----------

dfAirlines.write.format('com.databricks.spark.sqldw')\
  .option('url', conn_string)\
  .option('tempDir', 'abfss://' + adlscontainer + '@' + storage_account + '.dfs.core.windows.net/airlinestmp')\
  .option('forwardSparkAzureStorageCredentials', 'true')\
  .option('dbTable', 'dbo.Airlines')\
  .mode('overwrite')\
  .save()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Synapse Analytics Direct Access
# MAGIC #### First we create a table with some data

# COMMAND ----------

# MAGIC %sql
# MAGIC drop table if exists airports;
# MAGIC 
# MAGIC create table airports (
# MAGIC   city string,
# MAGIC   country string,
# MAGIC   icao string
# MAGIC );
# MAGIC 
# MAGIC insert into airports values ('Sydney', 'Australia', 'YSSY');
# MAGIC insert into airports values ('Los Angeles', 'USA', 'KLAX');
# MAGIC insert into airports values ('Singapore', 'Singapore', 'WSSS');
# MAGIC insert into airports values ('Tokyo', 'Japan', 'RJTT');
# MAGIC insert into airports values ('London', 'UK', 'EGLL');

# COMMAND ----------

# MAGIC %sql select * from airports

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS SYNairports;
# MAGIC 
# MAGIC 
# MAGIC CREATE TABLE SYNairports
# MAGIC USING com.databricks.spark.sqldw
# MAGIC OPTIONS (
# MAGIC   url "${synapse.conn_string}",
# MAGIC   forwardSparkAzureStorageCredentials 'true',
# MAGIC   dbTable 'Airports',
# MAGIC   tempDir "wasbs://synapsetemp@${adls.accountname}.blob.core.windows.net/"
# MAGIC )
# MAGIC AS SELECT * FROM airports;

# COMMAND ----------

# MAGIC %sql
# MAGIC insert into SYNairports values ('Frankfurt', 'Germany', 'EDDF');

# COMMAND ----------

# MAGIC %sql
# MAGIC drop table SYNairports

# COMMAND ----------

# MAGIC %md
# MAGIC ### Streaming Support

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql import *
from pyspark.sql.types import *

inputPath = "/databricks-datasets/structured-streaming/events/"
jsonSchema = StructType([ StructField("time", TimestampType(), True), StructField("action", StringType(), True) ])

def writeToSQLWarehouse(df, epochId):
  df.write.format("com.databricks.spark.sqldw") \
    .mode('overwrite') \
    .option('url', conn_string)\
    .option('tempDir', 'abfss://' + adlscontainer + '@' + storage_account + '.dfs.core.windows.net/streamtmp')\
    .option('forwardSparkAzureStorageCredentials', 'true')\
    .option('dbTable', 'dbo.StreamCounts')\
    .option('checkpointLocation', '/tmp_checkpoint_location')\
    .save()

spark.conf.set("spark.sql.shuffle.partitions", "1")

query = (
  spark.readStream.schema(jsonSchema)               # Set the schema of the JSON data
    .option("maxFilesPerTrigger", 1)  # Treat a sequence of files as a stream by picking one file at a time
    .json(inputPath)
    .selectExpr("action")
    .groupBy("action")
    .count()
    .toDF("action", "count")
    .writeStream
    .foreachBatch(writeToSQLWarehouse)
    .outputMode("update")
    .start()
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ### Read the table and create a Spark Dataframe
# MAGIC ##### The Synapse Data Warehouse needs to be active for the following queries to work
# MAGIC 
# MAGIC ### Create a MASTER KEY in Synapse before running this command
# MAGIC ALTER MASTER KEY REGENERATE WITH ENCRYPTION BY PASSWORD = 'P@ssword!!';

# COMMAND ----------

dfAirliners = spark.read.format('com.databricks.spark.sqldw')\
  .option('url', conn_string)\
  .option('tempDir', 'wasbs://'+adlscontainer+'@'+storage_account+'.blob.core.windows.net/')\
  .option('forwardSparkAzureStorageCredentials', 'true')\
  .option('dbTable', 'dbo.Airlines')\
  .load()

display(dfAirliners)



# COMMAND ----------

# MAGIC %md
# MAGIC #### Passing a query to Synapse DW for selective data load

# COMMAND ----------

df4engined = spark.read.format("com.databricks.spark.sqldw")\
  .option('url', conn_string)\
  .option('tempDir', 'wasbs://'+adlscontainer+'@'+storage_account+'.blob.core.windows.net/')\
  .option('forwardSparkAzureStorageCredentials', 'true')\
  .option("query", "select name, age from dbo.Airlines where country = 'UK'") \
  .load()

display(df4engined)

# COMMAND ----------

dbutils.notebook.exit("stop")
