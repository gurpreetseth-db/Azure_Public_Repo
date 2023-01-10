# Databricks notebook source
# MAGIC %md <a href='$../Azure Integrations Start Here'>Home</a>

# COMMAND ----------

# MAGIC %md # End to End Industrial IoT (IIoT) on Azure Databricks 
# MAGIC ## Part 2 - Machine Learning
# MAGIC This notebook demonstrates the following architecture for IIoT Ingest, Processing and Analytics on Azure. The following architecture is implemented for the demo. 
# MAGIC <img src="https://sguptasa.blob.core.windows.net/random/iiot_blog/end_to_end_architecture.png" width=800>
# MAGIC 
# MAGIC The notebook is broken into sections following these steps:
# MAGIC 3. **Machine Learning** - train XGBoost regression models using distributed ML to predict power output and asset remaining life on historical sensor data
# MAGIC 4. **Model Deployment** - deploy trained models for real-time serving in Azure ML services 
# MAGIC 5. **Model Inference** - score real data instantly against hosted models via REST API

# COMMAND ----------

# AzureML Workspace info (name, region, resource group and subscription ID) for model deployment
dbutils.widgets.text("Subscription ID","<your Azure subscription ID>","Subscription ID")
dbutils.widgets.text("Resource Group","<your Azure resource group name>","Resource Group")
dbutils.widgets.text("Region","<your Azure region>","Region")
dbutils.widgets.text("Storage Account","<your ADLS Gen 2 account name>","Storage Account")

# COMMAND ----------

# MAGIC %md ## Step 1 - Environment Setup
# MAGIC 
# MAGIC The pre-requisites are listed below:
# MAGIC 
# MAGIC ### Azure Services Required
# MAGIC * ADLS Gen 2 Storage account with a container called `iot`
# MAGIC * Azure Machine Learning Workspace called `iot`
# MAGIC 
# MAGIC ### Azure Databricks Configuration Required
# MAGIC * 3-node (min) Databricks Cluster running **DBR 7.0ML+** and the following libraries:
# MAGIC  * **MLflow[AzureML]** - PyPI library `azureml-mlflow`
# MAGIC  * **Azure Event Hubs Connector for Databricks** - Maven coordinates `com.microsoft.azure:azure-eventhubs-spark_2.12:2.3.16`
# MAGIC * The following Secrets defined in scope `iot`
# MAGIC  * `adls_key` - Access Key to ADLS storage account **(Important - use the [Access Key](https://raw.githubusercontent.com/tomatoTomahto/azure_databricks_iot/master/bricks.com/blog/2020/03/27/data-exfiltration-protection-with-azure-databricks.html))**
# MAGIC * The following notebook widgets populated:
# MAGIC  * `Subscription ID` - subscription ID of your Azure ML Workspace
# MAGIC  * `Resource Group` - resource group name of your Azure ML Workspace
# MAGIC  * `Region` - Azure region of your Azure ML Workspace
# MAGIC  * `Storage Account` - Name of your storage account
# MAGIC * **Part 1 Notebook Run to generate and process the data** (this can be found [here](https://databricks.com/notebooks/iiot/iiot-end-to-end-part-1.html)). Ensure the following tables have been created:
# MAGIC  * **turbine_maintenance** - Maintenance dates for each Wind Turbine
# MAGIC  * **turbine_power** - Hourly power output for each Wind Turbine
# MAGIC  * **turbine_enriched** - Hourly turbine sensor readinigs (RPM, Angle) enriched with weather readings (temperature, wind speed/direction, humidity)
# MAGIC  * **gold_readings** - Combined view containing all 3 tables

# COMMAND ----------

pip install azureml-sdk

# COMMAND ----------

# Setup access to storage account for temp data when pushing to Synapse
storage_account = dbutils.widgets.get("Storage Account")
spark.conf.set(f"fs.azure.account.key.{storage_account}.dfs.core.windows.net", dbutils.secrets.get("gsethi-kv-scope","gsethi-storage-secret"))

# Setup storage locations for all data
ROOT_PATH = f"abfss://iot@{storage_account}.dfs.core.windows.net/"

# Pyspark and ML Imports
import os, json, requests
from pyspark.sql import functions as F
from pyspark.sql.functions import pandas_udf, PandasUDFType
import numpy as np 
import pandas as pd
import xgboost as xgb
import mlflow.xgboost
import mlflow.azureml
from azureml.core import Workspace
from azureml.core.webservice import AciWebservice, Webservice
import random, string
from azureml.core.authentication import ServicePrincipalAuthentication

# Random String generator for ML models served in AzureML
random_string = lambda length: ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(length))

# COMMAND ----------

# MAGIC %sql
# MAGIC use iot;

# COMMAND ----------

# MAGIC %md ## Step 3 - Machine Learning
# MAGIC Now that our data is flowing reliably from our sensor devices into an enriched Delta table in Data Lake storage, we can start to build ML models to predict power output and remaining life of our assets using historical sensor, weather, power and maintenance data. 
# MAGIC 
# MAGIC We create two models ***for each Wind Turbine***:
# MAGIC 1. Turbine Power Output - using current readings for turbine operating parameters (angle, RPM) and weather (temperature, humidity, etc.), predict the expected power output 6 hours from now
# MAGIC 2. Turbine Remaining Life - predict the remaining life in days until the next maintenance event
# MAGIC 
# MAGIC <img src="https://sguptasa.blob.core.windows.net/random/iiot_blog/turbine_models.png" width=800>
# MAGIC 
# MAGIC We will use the XGBoost framework to train regression models. Due to the size of the data and number of Wind Turbines, we will use Spark UDFs to distribute training across all the nodes in our cluster.

# COMMAND ----------

# MAGIC %md ### 3a. Feature Engineering
# MAGIC In order to predict power output 6 hours ahead, we need to first time-shift our data to create our label column. We can do this easily using Spark Window partitioning. 
# MAGIC 
# MAGIC In order to predict remaining life, we need to backtrace the remaining life from the maintenance events. We can do this easily using cross joins. The following diagram illustrates the ML Feature Engineering pipeline:
# MAGIC 
# MAGIC <img src="https://sguptasa.blob.core.windows.net/random/iiot_blog/ml_pipeline.png" width=800>

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Calculate the age of each turbine and the remaining life in days
# MAGIC CREATE OR REPLACE VIEW turbine_age AS
# MAGIC WITH reading_dates AS (SELECT distinct date, deviceid FROM turbine_power),
# MAGIC   maintenance_dates AS (
# MAGIC     SELECT d.*, datediff(nm.date, d.date) as datediff_next, datediff(d.date, lm.date) as datediff_last 
# MAGIC     FROM reading_dates d LEFT JOIN turbine_maintenance nm ON (d.deviceid=nm.deviceid AND d.date<=nm.date)
# MAGIC     LEFT JOIN turbine_maintenance lm ON (d.deviceid=lm.deviceid AND d.date>=lm.date ))
# MAGIC SELECT date, deviceid, ifnull(min(datediff_last),0) AS age, ifnull(min(datediff_next),0) AS remaining_life
# MAGIC FROM maintenance_dates 
# MAGIC GROUP BY deviceid, date;
# MAGIC 
# MAGIC -- Calculate the power 6 hours ahead using Spark Windowing and build a feature_table to feed into our ML models
# MAGIC CREATE OR REPLACE VIEW feature_table AS
# MAGIC SELECT r.*, age, remaining_life,
# MAGIC   LEAD(power, 72, power) OVER (PARTITION BY r.deviceid ORDER BY window) as power_6_hours_ahead
# MAGIC FROM gold_readings r JOIN turbine_age a ON (r.date=a.date AND r.deviceid=a.deviceid)
# MAGIC WHERE r.date < CURRENT_DATE();

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT window, power, power_6_hours_ahead FROM feature_table WHERE deviceid='WindTurbine-1'

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT date, avg(age) as age, avg(remaining_life) as life FROM feature_table WHERE deviceid='WindTurbine-1' GROUP BY date ORDER BY date

# COMMAND ----------

# MAGIC %md ### 3b. Distributed Model Training - Predict Power Output
# MAGIC [Pandas UDFs](https://docs.microsoft.com/en-us/azure/databricks/spark/latest/spark-sql/udf-python-pandas?toc=https%3A%2F%2Fdocs.microsoft.com%2Fen-us%2Fazure%2Fazure-databricks%2Ftoc.json&bc=https%3A%2F%2Fdocs.microsoft.com%2Fen-us%2Fazure%2Fbread%2Ftoc.json) allow us to vectorize Pandas code across multiple nodes in a cluster. Here we create a UDF to train an XGBoost Regressor model against all the historic data for a particular Wind Turbine. We use a Grouped Map UDF as we perform this model training on the Wind Turbine group level.

# COMMAND ----------

# Create a function to train a XGBoost Regressor on a turbine's data
def train_distributed_xgb(readings_pd, model_type, label_col, prediction_col):
  mlflow.xgboost.autolog()
  with mlflow.start_run():
    # Log the model type and device ID
    mlflow.log_param('deviceid', readings_pd['deviceid'][0])
    mlflow.log_param('model', model_type)

    # Train an XGBRegressor on the data for this Turbine
    alg = xgb.XGBRegressor() 
    train_dmatrix = xgb.DMatrix(data=readings_pd[feature_cols].astype('float'),label=readings_pd[label_col])
    params = {'learning_rate': 0.5, 'alpha':10, 'colsample_bytree': 0.5, 'max_depth': 5}
    model = xgb.train(params=params, dtrain=train_dmatrix, evals=[(train_dmatrix, 'train')])

    # Make predictions on the dataset and return the results
    readings_pd[prediction_col] = model.predict(train_dmatrix)
  return readings_pd

# Create a Spark Dataframe that contains the features and labels we need
non_feature_cols = ['date','window','deviceid','winddirection','remaining_life']
feature_cols = ['angle','rpm','temperature','humidity','windspeed','power','age']
label_col = 'power_6_hours_ahead'
prediction_col = label_col + '_predicted'

# Read in our feature table and select the columns of interest
feature_df = spark.table('feature_table').selectExpr(non_feature_cols + feature_cols + [label_col] + [f'0 as {prediction_col}'])

# Register a Pandas UDF to distribute XGB model training using Spark
@pandas_udf(feature_df.schema, PandasUDFType.GROUPED_MAP)
def train_power_models(readings_pd):
  return train_distributed_xgb(readings_pd, 'power_prediction', label_col, prediction_col)

# Run the Pandas UDF against our feature dataset - this will train 1 model for each turbine
power_predictions = feature_df.groupBy('deviceid').apply(train_power_models)

# Save predictions to storage
power_predictions.write.format("delta").mode("overwrite").partitionBy("date").saveAsTable("turbine_power_predictions")

# COMMAND ----------

# MAGIC %sql 
# MAGIC -- Plot actuals vs. predicted
# MAGIC SELECT date, deviceid, avg(power_6_hours_ahead) as actual, avg(power_6_hours_ahead_predicted) as predicted FROM turbine_power_predictions GROUP BY date, deviceid

# COMMAND ----------

# MAGIC %md #### Automated Model Tracking in Databricks
# MAGIC As you train the models, notice how Databricks-managed MLflow automatically tracks each run in the "Runs" tab of the notebook. You can open each run and view the parameters, metrics, models and model artifacts that are captured by MLflow Autologging. For XGBoost Regression models, MLflow tracks: 
# MAGIC 1. Any model parameters (alpha, colsample, learning rate, etc.) passed to the `params` variable
# MAGIC 2. Metrics specified in `evals` (RMSE by default)
# MAGIC 3. The trained XGBoost model file
# MAGIC 4. Feature importances
# MAGIC 
# MAGIC <img src="https://sguptasa.blob.core.windows.net/random/iiot_blog/iiot_mlflow_tracking.gif" width=800>

# COMMAND ----------

# MAGIC %md ### 3c. Distributed Model Training - Predict Remaining Life
# MAGIC Our second model predicts the remaining useful life of each Wind Turbine based on the current operating conditions. We have historical maintenance data that indicates when a replacement activity occured - this will be used to calculate the remaining life as our training label. 
# MAGIC 
# MAGIC Once again, we train an XGBoost model for each Wind Turbine to predict the remaining life given a set of operating parameters and weather conditions

# COMMAND ----------

# Create a Spark Dataframe that contains the features and labels we need
non_feature_cols = ['date','window','deviceid','winddirection','power_6_hours_ahead_predicted']
label_col = 'remaining_life'
prediction_col = label_col + '_predicted'

# Read in our feature table and select the columns of interest
feature_df = spark.table('turbine_power_predictions').selectExpr(non_feature_cols + feature_cols + [label_col] + [f'0 as {prediction_col}'])

# Register a Pandas UDF to distribute XGB model training using Spark
@pandas_udf(feature_df.schema, PandasUDFType.GROUPED_MAP)
def train_life_models(readings_pd):
  return train_distributed_xgb(readings_pd, 'life_prediction', label_col, prediction_col)

# Run the Pandas UDF against our feature dataset - this will train 1 model per turbine and write the predictions to a table
life_predictions = (
  feature_df.groupBy('deviceid').apply(train_life_models)
    .write.format("delta").mode("overwrite")
    .partitionBy("date")
    .saveAsTable("turbine_life_predictions")
)

# COMMAND ----------

# MAGIC %sql 
# MAGIC SELECT date, avg(remaining_life) as Actual_Life, avg(remaining_life_predicted) as Predicted_Life 
# MAGIC FROM turbine_life_predictions 
# MAGIC WHERE deviceid='WindTurbine-1' 
# MAGIC GROUP BY date ORDER BY date

# COMMAND ----------

# MAGIC %md The models to predict remaining useful life have been trained and logged by MLflow. We can now move on to model deployment in AzureML.

# COMMAND ----------

# MAGIC %md ## Step 4 - Model Deployment to AzureML
# MAGIC Now that our models have been trained, we can deploy them in an automated way directly to a model serving environment like Azure ML. Below, we connect to an AzureML workspace, build a container image for the model, and deploy that image to Azure Container Instances (ACI) to be hosted for REST API calls. 
# MAGIC 
# MAGIC **Note:** This step can take up to 10 minutes to run due to images being created and deplyed in Azure ML.
# MAGIC 
# MAGIC **Important:** This step requires authentication to Azure - open the link provided in the output of the cell in a new browser tab and use the code provided.

# COMMAND ----------

# AML Workspace Information - replace with your workspace info
aml_resource_group = dbutils.widgets.get("Resource Group")
aml_subscription_id = dbutils.widgets.get("Subscription ID")
aml_region = dbutils.widgets.get("Region")
aml_workspace_name = "iot"
turbine = "WindTurbine-1"
power_model = "power_prediction"
life_model = "life_prediction"

tenn_id = "9f37a392-f0ae-4280-9796-f1864a10effc"
sp_id = dbutils.secrets.get("iot","iot-ml-clid") # ClientId
sp_pw = dbutils.secrets.get("iot","iot-ml-sp") # Get SP password from secrets

# Service Pricipal authentication
sp = ServicePrincipalAuthentication(tenant_id=tenn_id, # tenantID
                                    service_principal_id=sp_id, # clientId
                                    service_principal_password=sp_pw) # clientSecret

# Connect to a workspace (replace widgets with your own workspace info)
workspace = Workspace.create(name = aml_workspace_name,
                             subscription_id = aml_subscription_id,
                             resource_group = aml_resource_group,
                             location = aml_region,
                             auth=sp,
                             exist_ok=True)

# Retrieve the remaining_life and power_output experiments on WindTurbine-1, and get the best performing model (min RMSE)
best_life_model = mlflow.search_runs(filter_string=f'params.deviceid="{turbine}" and params.model="{life_model}"')\
  .dropna().sort_values("metrics.train-rmse")['artifact_uri'].iloc[0] + '/model'
best_power_model = mlflow.search_runs(filter_string=f'params.deviceid="{turbine}" and params.model="{power_model}"')\
  .dropna().sort_values("metrics.train-rmse")['artifact_uri'].iloc[0] + '/model'

scoring_uris = {}
for model, path in [('life',best_life_model),('power',best_power_model)]:
  # Build images for each of our two models in Azure Container Instances
  print(f"-----Building image for {model} model-----")
  model_image, azure_model = mlflow.azureml.build_image(model_uri=path, 
                                                        workspace=workspace, 
                                                        model_name=model,
                                                        image_name=model,
                                                        description=f"XGBoost model to predict {model} of a turbine", 
                                                        synchronous=True)
  model_image.wait_for_creation(show_output=True)

  # Deploy web services to host each model as a REST API
  print(f"-----Deploying image for {model} model-----")
  dev_webservice_name = model + random_string(10)
  dev_webservice_deployment_config = AciWebservice.deploy_configuration()
  dev_webservice = Webservice.deploy_from_image(name=dev_webservice_name, image=model_image, deployment_config=dev_webservice_deployment_config, workspace=workspace)
  dev_webservice.wait_for_deployment()

  # Get the URI for sending REST requests to
  scoring_uris[model] = dev_webservice.scoring_uri

# COMMAND ----------

print(f"-----Model URIs for Scoring:-----")
print(f"Life Prediction URL: {scoring_uris['life']}")
print(f"Power Prediction URL: {scoring_uris['power']}")

# COMMAND ----------

# MAGIC %md You can view your model, it's deployments and URL endpoints by navigating to https://ml.azure.com/.
# MAGIC 
# MAGIC <img src="https://sguptasa.blob.core.windows.net/random/iiot_blog/iiot_azureml.gif" width=800>

# COMMAND ----------

# MAGIC %md ## Step 5 - Model Inference: Real-time Scoring
# MAGIC We can now make HTTP REST calls from a web app, PowerBI, or directly from Databricks to the hosted model URI to score data directly

# COMMAND ----------

# Retrieve the Scoring URL provided by AzureML
power_uri = scoring_uris['power'] 
life_uri = scoring_uris['life'] 

# Construct a payload to send with the request
payload = {
  'angle':8,
  'rpm':6,
  'temperature':25,
  'humidity':50,
  'windspeed':5,
  'power':150,
  'age':10
}

def score_data(uri, payload):
  rest_payload = json.dumps({"data": [list(payload.values())]})
  response = requests.post(uri, data=rest_payload, headers={"Content-Type": "application/json"})
  return json.loads(response.text)

print(f'Current Operating Parameters: {payload}')
print(f'Predicted power (in kwh) from model: {score_data(power_uri, payload)}')
print(f'Predicted remaining life (in days) from model: {score_data(life_uri, payload)}')

# COMMAND ----------

# MAGIC %md ### Step 6: Asset Optimization
# MAGIC We can now identify the optimal operating conditions for maximizing power output while also maximizing asset useful life. 
# MAGIC 
# MAGIC \\(Revenue = Price\displaystyle\sum_1^{365} Power_t\\)
# MAGIC 
# MAGIC \\(Cost = {365 \over Life_{rpm}} Price \displaystyle\sum_1^{24} Power_t \\)
# MAGIC 
# MAGIC \\(Profit = Revenue - Cost\\)
# MAGIC 
# MAGIC \\(Power_t\\) and \\(Life\\) will be calculated by scoring many different RPM values in AzureML. The results can be visualized to identify the RPM that yields the highest profit.

# COMMAND ----------

# Construct a payload to send with the request
payload = {
  'angle':8,
  'rpm':6,
  'temperature':25,
  'humidity':50,
  'windspeed':5,
  'power':150,
  'age':10
}

# Iterate through 50 different RPM configurations and capture the predicted power and remaining life at each RPM
results = []
for rpm in range(1,15):
  payload['rpm'] = rpm
  expected_power = score_data(power_uri, payload)[0]
  payload['power'] = expected_power
  expected_life = -score_data(life_uri, payload)[0]
  results.append((rpm, expected_power, expected_life))
  
# Calculalte the Revenue, Cost and Profit generated for each RPM configuration
optimization_df = pd.DataFrame(results, columns=['RPM', 'Expected Power', 'Expected Life'])
optimization_df['Revenue'] = optimization_df['Expected Power'] * 24 * 365
optimization_df['Cost'] = optimization_df['Expected Power'] * 24 * 365 / optimization_df['Expected Life']
optimization_df['Profit'] = optimization_df['Revenue'] + optimization_df['Cost']

display(optimization_df)

# COMMAND ----------

# MAGIC %md The optimal operating parameters for **WindTurbine-1** given the specified weather conditions is **11 RPM** for generating a maximum profit of **$1.4M**! Your results may vary due to the random nature of the sensor readings. 

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 7: Data Serving and Visualization (not included in notebook)
# MAGIC Now that our models are created and the data is scored, we can use Azure Synapse with PowerBI to perform data warehousing and analyltic reporting to generate a report like the one below. 
# MAGIC <img src="https://sguptasa.blob.core.windows.net/random/iiot_blog/PBI_report.gif" width=800>

# COMMAND ----------


