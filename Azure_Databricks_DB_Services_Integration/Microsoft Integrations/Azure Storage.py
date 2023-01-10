# Databricks notebook source
# MAGIC %md <a href='$../Azure Integrations Start Here'>Home</a>

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC ## PLEASE COPY *sample_data.json* file from *datasets* folder to your blog storage before continue further.

# COMMAND ----------

# MAGIC %md
# MAGIC # Azure Storage

# COMMAND ----------

# MAGIC %md ## Azure Blob Storage

# COMMAND ----------

# MAGIC %md #### Using a Storage Account Key (SAS)
# MAGIC * Provide Storage Account Name
# MAGIC * Container Name
# MAGIC * SAS Key Value

# COMMAND ----------

# Populate required variables below

akv_secret_scope = "Databricks-KeyVault-Scope" # The Azure Key Vault Secret Scope which is created automatically as part of Terraform deployment
akv_storage_account = "storage-account-name" # The Azure Key Vault secret key name corresponding to storge which is created automatically as part of Terraform deployment
akv_storage_access_key = "storage-access-key" # The Azure Key Vault secret key name corresponding to storge access key which is created automatically as part of Terraform deployment


storage_account_name = dbutils.secrets.get(scope = akv_secret_scope, key = akv_storage_account)
storage_account_access_key = dbutils.secrets.get(scope = akv_secret_scope, key = akv_storage_access_key)
storage_container = "datasets"

filename = 'sample_data.json'

# COMMAND ----------


file_location = "wasbs://" + storage_container + "@" + storage_account_name + ".blob.core.windows.net/"
file_type = "json"
spark.conf.set("fs.azure.account.key."+storage_account_name+".blob.core.windows.net", storage_account_access_key)


df = spark.read.format(file_type).option("inferSchema", "true").load(file_location + filename)
df.head(5)

# COMMAND ----------

# MAGIC %md #### Using a secret stored in Azure Key Vault
# MAGIC 
# MAGIC ```
# MAGIC akv_secret_scope = "SECRET SCOPE NAME" 
# MAGIC akv_secret_key = "SECRET KEY" # The AKV secret key name corresponding to the secret
# MAGIC storage_account_name = "STORAGE ACCOUNT"
# MAGIC storage_container = "datasets"
# MAGIC file_location = "wasbs://" + storage_container + "@" + storage_account_name + ".blob.core.windows.net/"
# MAGIC spark.conf.set(
# MAGIC     "fs.azure.account.key."+storage_account_name+".blob.core.windows.net",  
# MAGIC     dbutils.secrets.get(scope = akv_secret_scope, key = akv_secret_key)
# MAGIC )
# MAGIC 
# MAGIC filename = 'sample_data.json'
# MAGIC df = spark.read.format(file_type).option("inferSchema", "true").load(file_location + filename)
# MAGIC df.head(5)
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC #### Using a Shared Access Signature (SAS) Directly

# COMMAND ----------

dbutils.widgets.text('Shared Access Signature URL', '')

dbutils.widgets.text('Shared Access Signature Token', '')

# COMMAND ----------

# Seems either sas_blob or sas will work
sas_blob = dbutils.widgets.get('Shared Access Signature URL')  
sas = dbutils.widgets.get('Shared Access Signature Token')

file_location = "wasbs://" + storage_container + "@" + storage_account_name + ".blob.core.windows.net/"
file_type = "json"
spark.conf.set(
  "fs.azure.sas."+storage_container+"."+storage_account_name+".blob.core.windows.net",
  sas_blob)

df = spark.read.format(file_type).option("inferSchema", "true").load(file_location + filename)
df.head(5)

# COMMAND ----------

# MAGIC %md #### Mounting a Blob Storage Account

# COMMAND ----------

#extra_configs = {f"fs.azure.account.key.{storage_account_name}.blob.core.windows.net":storage_account_name}

dbutils.fs.mount(
  source = "wasbs://datasets@"+storage_account_name+".blob.core.windows.net",
  mount_point = "/mnt/datasets",
  extra_configs = {"fs.azure.sas."+storage_container+"."+storage_account_name+".blob.core.windows.net":sas}
)

# COMMAND ----------

# MAGIC %sh ls -l /dbfs/mnt/datasets

# COMMAND ----------

# MAGIC %md
# MAGIC ### Write JSON data as Delta Table - Used in ADLSGen2 example below

# COMMAND ----------

df = spark.read.format(file_type).option("inferSchema", "true").load(file_location + filename)

df.write.mode("overwrite").format("delta").save('/mnt/datasets/sample_data')


# COMMAND ----------

# MAGIC %md ## Azure Data Lake Storage Generation Two (ADLSg2)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Direct access via Storage Account Key

# COMMAND ----------

# Set up direct account access key

adlsloc = 'abfss://' + storage_container + '@' + storage_account_name + '.dfs.core.windows.net/'

# COMMAND ----------

spark.conf.set(
  'fs.azure.account.key.' + storage_account_name + '.dfs.core.windows.net',storage_account_access_key
)

# COMMAND ----------

df = spark.read.load(adlsloc + 'sample_data', format='delta')

# COMMAND ----------

df.printSchema()

# COMMAND ----------

display(df)

# COMMAND ----------

df.createOrReplaceTempView('ksptelem')

# COMMAND ----------

# MAGIC %sql
# MAGIC select avg(alt), utime from ksptelem group by utime

# COMMAND ----------

# MAGIC %md
# MAGIC ##CREATE A *CREDENTIAL PASS THROUGH CLUSTER* AND GRANT YOURSELF *STRORGE BLOB DATA CONTRIBUTOR* ROLE AT STORAGE

# COMMAND ----------

# MAGIC %md
# MAGIC ## Mounting an ADLSg2 Storage Container on a DBFS mount point
# MAGIC ### First example uses AAD Credential Passthrough
# MAGIC ##### Which means the cluster must have credential passthrough enabled or it will fail.
# MAGIC ##### Also - Note that the user credential needs to have the "Storage Blob Data Contributor" AD role on the container to be able to read the data - being Owner is not enough! Owner only gives you rights to manage the container, but not access the contents of the container. Also applicable to SP below.

# COMMAND ----------

# Unmount if already mounted
dbutils.fs.unmount('/mnt/datasets')

# COMMAND ----------

configs = {
  "fs.azure.account.auth.type": "CustomAccessToken",
  "fs.azure.account.custom.token.provider.class":   spark.conf.get("spark.databricks.passthrough.adls.gen2.tokenProviderClassName")
}
dbutils.fs.mount(
  source = "abfss://"+storage_container+"@"+storage_account_name+".dfs.core.windows.net/",
  mount_point = "/mnt/datasets",
  extra_configs = configs)

# COMMAND ----------

dbutils.fs.ls('/mnt/datasets')

# COMMAND ----------

dbutils.fs.unmount('/mnt/datasets')

# COMMAND ----------

# MAGIC %sh
# MAGIC ls /dbfs/mnt/datasets

# COMMAND ----------

# MAGIC %md
# MAGIC ##Need to Create a Azure AD Service Principal For This Code Snippet to Execute

# COMMAND ----------

# MAGIC %md
# MAGIC ### This next example uses Azure AD Service Principals
# MAGIC ##### Note that the SP needs to have the "Storage Blob Data Contributor" AD role on the container to be able to read the data - being Owner is not enough! Owner only gives you rights to manage the container, but not access the contents of the container.

# COMMAND ----------

# MAGIC %md
# MAGIC <pre>
# MAGIC configs = {"fs.azure.account.auth.type": "OAuth",
# MAGIC            "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
# MAGIC            "fs.azure.account.oauth2.client.id": "[application-id]",
# MAGIC            "fs.azure.account.oauth2.client.secret": dbutils.secrets.get(scope="[scope-name]",key="[service-credential-key-name]"),
# MAGIC            "fs.azure.account.oauth2.client.endpoint": "https://login.microsoftonline.com/[directory-id]/oauth2/token"}
# MAGIC 
# MAGIC dbutils.fs.mount(
# MAGIC   source = "abfss://deltalake@jokdemoresourcesadls.dfs.core.windows.net/",
# MAGIC   mount_point = "/mnt/deltalake",
# MAGIC   extra_configs = configs)
# MAGIC </pre>

# COMMAND ----------

configs = {"fs.azure.account.auth.type": "OAuth",
             "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
            "fs.azure.account.oauth2.client.id": dbutils.secrets.get(scope="Databricks-KeyVault-Scope",key="Azure-App-Registration-ClientID"),
           "fs.azure.account.oauth2.client.secret": dbutils.secrets.get(scope="Databricks-KeyVault-Scope",key="Azure-App-Registration-Client-Secret"),
          "fs.azure.account.oauth2.client.endpoint": "https://login.microsoftonline.com/9f37a392-f0ae-4280-9796-f1864a10effc/oauth2/token"}


dbutils.fs.mount(
  source = "abfss://"+storage_container+"@"+storage_account_name+".dfs.core.windows.net/",
  mount_point = "/mnt/datasets",
  extra_configs = configs)


# COMMAND ----------

# MAGIC %sh
# MAGIC ls -l /dbfs/mnt/datasets

# COMMAND ----------

# MAGIC %sh
# MAGIC head /dbfs/mnt/datasets/sample_data.json

# COMMAND ----------

dbutils.fs.unmount('/mnt/datasets')

# COMMAND ----------

# MAGIC %md
# MAGIC Remove Widgets

# COMMAND ----------


dbutils.widgets.remove('Shared Access Signature URL')

dbutils.widgets.remove('Shared Access Signature Token')

# COMMAND ----------

# MAGIC %md
# MAGIC ### Deprecated Storage Patterns
# MAGIC https://learn.microsoft.com/en-us/azure/databricks/external-data/azure-storage#deprecated-patterns-for-storing-and-accessing-data-from-azure-databricks
# MAGIC 
# MAGIC * Databricks no longer recommends mounting external data locations to Databricks Filesystem.
# MAGIC * Databricks no longer recommends Access Azure Data Lake Storage using Azure Active Directory credential passthrough.
# MAGIC * The legacy Windows Azure Storage Blob driver (WASB) has been deprecated. ABFS has numerous benefits over WASB. 
# MAGIC * Azure has announced the pending retirement of Azure Data Lake Storage Gen1. Azure Databricks recommends migrating all Azure Data Lake Storage Gen1 to Azure Data Lake Storage Gen2. If you have not yet migrated.
