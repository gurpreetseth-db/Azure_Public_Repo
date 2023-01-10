# Azure Databricks and Integration with Other Azure Database Services

This repository is primarily to demostrate as how to integrate Azure Databricks with other Azure Database & other Services like:

  1) Azure Storage
  2) Azure Key Vault
  3) Azure SQL Server
  4) Azure Synapse
  5) Azure CosmosDB
  6) Azure EVenthub
  
## Folder Structure

Below are the main files and folders in this repository

| Name                                            | File/Folder  | Description                                   |
| ----------------------------------------------- | ------------ | --------------------------------------------- |
| `Azure Integration Starts Here`                 | File         | Main File with links to rest of the demo |
| `datasets`                                      | Folder       | consists of sample data files which will be used in the notebooks |
| `Include`                                       | Folder       | consists of initialisation scripts to create common functions that are used in the notebook |
| `Microsoft Integration`                         | Folder       | main folder, conssist of most of the notebooks that we will be using for demostration | | `Koalas`                                        | Folder       | has notebook to demostrate Koala language. |
| `Notebook DeepDive`                             | Folder       | consist of notebook to demostrate databricks basic features |
| `Modern Industraial IOT with Azure Databricks`  | Folder       | Work in Progress    |
| `Delta Lake`                                    | Folder       | Work in Progress    | 


## Getting Started

  1. Make sure that Azure Environment is ready. Leverage terraform scripts from this repo https://github.com/gurpreetseth-db/Azure_Public_Repo/tree/main/Azure_Databricks_Other_DB_Services_Basic 
  2. Clone this repo to your Databricks Environment
  3. Click on `"Azure Integration Starts Here"` notebook and follow along
  
## Databricks Clusters

There shall be 2 clusters deployed for you (if used terraform setup scripts as mentioned in Getting Started - Point 1)

![image](https://user-images.githubusercontent.com/95003669/211474677-bc2bc4ca-eab0-43bf-86f9-d19e8733bafa.png)

**Note**
Please use **Single User - Cosmosdb** cluster for running Cosmodb notebook.


    
  
