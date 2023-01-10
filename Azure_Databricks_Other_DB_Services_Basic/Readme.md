# Provisioning Azure Databricks and other common Azure Data Services via Terraform

This template provides an example deployment of Terraform Scripts to deploy Data Serivces in Azure (list below). This is basic / default installation which means interconnectivity of these services etc will be Azure Managed.

  1. Azure Resource Group
  2. Azure Databricks
  3. Azure Storage (ADLS Gen2)
  4. Azure Key Vault
  5. Azure CosmosDB
  6. Azure Event Hub
  7. Azure SQL Server & Database
  8. Azure Synapse Workspace


## Requirements

  | Name                                                                         | Version  |
  | ---------------------------------------------------------------------------- | -------- |
  | <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm)          | >=3.37.0 |
  | <a name="requirement_databricks"></a> [databricks](#requirement\_databricks) | 1.7.0    |

## Providers

  | Name                                                                    | Version |
  | ----------------------------------------------------------------------- | ------- |
  | <a name="provider_azurerm"></a> [azurerm](#provider\_azurerm)           | 3.37.0  |
  | <a name="provider_random"></a> [random](#provider\_random)              | 3.4.3   |
  | <a name="provider_databricks"></a> [databricks](#provider\_databricks)  | 1.17.0  |
  | <a name="provider_azureread"></a> [azureread](#provider\_azureread)     | 2.31.0  | 
  
  
## Getting Started

  1. Clone this repo to your local machine running terraform.
  2. Run `teraform init` to initialize terraform and get provider ready.
  3. Change `terraform.tfvars` and `variables.tf` values. Please check **How to fill in variable value** section next.
  4. Inside the local project folder, run `terraform apply` to create the resources.
  
## How to fill in variable values
In `variables.tf`, set these variables:

  | Variable Name                   | Values         | Description                                                                                        |
  | --------------------------------|-------------------------|------------------------------------------------------------------------------------------ |
  | name                            | First Name & Last Name  | First 3 character of Fist Name will be used to create as suffix for each deployed resources |
  | email                           | email address           | Which will be used to login to Azure Portal                                               |
  | rglocation                      | Azure Region            | Azure region where resources will be deployed. Default **australiasoutheast**             |
  | node_type                       | Databricks Node Type    | Default **Standard_DS3_V2**                                                               |   | global_auto_termination_minute  | Cluster termination min | Cluster ideal time for Databricks Cluster post which cluster will be shutdown (in minutes) |
  | no_public_ip                    | True/False              | Whether Databricks CLuster have Public IP or Not Default **false** which means it will have public ip - For future Vnet deployments | 
  
In `terraform.tfvars`, set these variables:

  | Variable Name                   | Values         | Description                                                                                        |
  | --------------------------------|-------------------------|------------------------------------------------------------------------------------------ |
  | name                            | First Name & Last Name  | First 3 character of Fist Name will be used to create as suffix for each deployed resources | 
  
## Post Deployment Steps

Post successful deployment, one shall see 9 resources deployed (check below screenshot)
  
  ![image](https://user-images.githubusercontent.com/95003669/211424156-255db7c2-6df8-4f4f-bae1-3979a936df17.png)
  
Open, Azure Key Vault -> Secrets and we shall see bunch of Secrets already saved. These secrets save information about environment like JDBC URLs, User ad Password details etc... which can be used in notebooks to connect to respective service.

**Note**, Secrets with name as **Azure-*** are Service Principal related which is not required but if want to test Azure Storage connectivity from Azure Databricks via Credential Pass Through then this is required. Follow process mentioned (below in this document) **Create Service Principal** for the same.

  ![image](https://user-images.githubusercontent.com/95003669/211460837-f8ccf763-e696-4682-89c9-4b6b892574d6.png)

 
Next, we need to 
 
1) **Grant Get & List access to Azure Databricks on Azure Key Vault**
  
   a. Open Azure Keyvault, Click on Access Policies
              
   ![image](https://user-images.githubusercontent.com/95003669/211451801-c73bbcac-9820-4558-8e4e-e8a396100352.png) 

   b. Click Create, From **Secret permissions**, select **Get, List** , click Next
   
   ![image](https://user-images.githubusercontent.com/95003669/211452037-6814dd99-678f-47ae-a707-2c4ac66bbc8b.png)

   c. Type in **AzureDatabricks** (No Space), Select **AzureDatabricks** from list and click Next
    
   ![image](https://user-images.githubusercontent.com/95003669/211452300-926e534d-33df-4a77-90c9-972c417208c2.png)
      
   d. Click, Next & Create
    
   ![image](https://user-images.githubusercontent.com/95003669/211452414-6f2a6d1e-f51c-458e-95c6-eb91c7d48e1a.png)

   e. Once done, shall see **AzureDatabricks** application **Get, List** permissions on **Secrets**
    
   ![image](https://user-images.githubusercontent.com/95003669/211452542-35f23130-b6b2-4318-b738-766f806ce528.png)
   
  2) **Update Firewall Rules for Azure SQL Server**
   
   a. Open Azure SQL Server, Under **Security**, Click **Networking**
   b. Under **Firewall rules**, Click **+Add your client IPv4 address (xxx.xxx.xxx.xxx)**
   c. Click **Save** 
   
   ![image](https://user-images.githubusercontent.com/95003669/211458629-c19a3ea5-4c20-4839-b965-92df8f5bb376.png)



## Resources Used
|  Name                                                                                                                                       | Type     |
| --------------------------------------------------------------------------------------------------------------------------------------------| ---------|
| [azurerm_resource_group.this](https://registry.terraform.io/providers/hashicorp/azurerm/2.83.0/docs/resources/resource_group)               | resource |
| [azurerm_databricks_workspace.example](https://registry.terraform.io/providers/hashicorp/azurerm/2.83.0/docs/resources/databricks_workspace)| resource |
| [azurerm_key_vault_secret.databricks_pat_token](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault)                      | resource |
| [azurerm_storage_account.example](https://registry.terraform.io/providers/hashicorp/azurerm/2.83.0/docs/resources/storage_account)          | resource |
| [azurerm_storage_container.example](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_container)      | resource | | [azurerm_storage_container.synapse](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_container)      | resource |
| [azurerm_storage_container.synapsetemp](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_container)  | resource |
| [azurerm_key_vault.example](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault)                      | resource |
| [azurerm_key_vault_secret.storageaccount](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_secret) | resource |
| [azurerm_key_vault_secret.storageacesskey](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_secret)| resource |
| [azurerm_mssql_server.example](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/mssql_server)                | resource |
| [azurerm_mssql_database.example](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/mssql_database)            | resource |
| [azurerm_key_vault_secret.url](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_secret)            | resource |
| [azurerm_key_vault_secret.user](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_secret)           | resource |
| [azurerm_key_vault_secret.password](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_secret)       | resource |
| [azurerm_storage_data_lake_gen2_filesystem.example](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_data_lake_gen2_filesystem)                | resource |
| [azurerm_synapse_workspace.example](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/synapse_workspace)      | resource |
| [azurerm_synapse_workspace_aad_admin.example](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/synapse_workspace_aad_admin)     | resource |
| [azurerm_synapse_sql_pool.example](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/synapse_sql_pool)       | resource |
| [azurerm_key_vault_secret.synapseurl](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_secret)            | resource |
| [azurerm_key_vault_secret.synapseuser](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_secret)           | resource |
| [azurerm_key_vault_secret.synapsepassword](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_secret)       | resource |
| [azurerm_cosmosdb_account.db](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/cosmosdb_account)            | resource |
| [azurerm_cosmosdb_sql_database.example](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/cosmosdb_sql_database)            | resource |
| [azurerm_key_vault_secret.cosmosdbendpoint](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_secret)           | resource |
| [azurerm_key_vault_secret.cosmosdbaccountkey](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_secret)       | resource |
| [azurerm_eventhub_namespace.example](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/eventhub_namespace)    | resource |
| [azurerm_eventhub.example](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/eventhub)    | resource |
| [azurerm_eventhub_authorization_rule.example](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/eventhub_authorization_rule)    | resource |
| [azurerm_key_vault_secret.eventhubstring](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_secret)       | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/client_config)       | datasource |


## Inputs

| Name                                                                               | Description              | Type        | Default      | Required |
| -----------------------------------------------------------------------------------|------------------------- | ----------- | ------------ | :------: |
| <a name="input_name"></a> [name](#input\_name)                                     | your name minimm 3 char  | `string`    | n/a          |    yes    |
| <a name="input_email"></a> [email](#input\_email)                                  | email as loged to Azure Portal | `string` | n/a       |   yes    |
| <a name="input_rglocation"></a> [rglocation](#input\_rglocation)                   | region for resource deployment | `string`    | `"australiasoutheast"` |    yes    |
| <a name="input_node_type"></a> [node\_type](#input\_node\_type)                    | databricks cluster type  | `string`    | `"Standard_DS3_v2"`               |   yes    |
| <a name="input_global_auto_termination_minute"></a> [global\_auto\_termination\_minute](#input\_global\_auto\_termination\_minute)         | cluster ideal time post which it will be shutdown        | `number`      | `"30`            |    no   |
| <a name="input_no_public_ip"></a> [no\_public\_ip](#input\_no\_public\_ip)                           | public ip for databricks (For Future Releases)         | `bool`    | `"false"` |    no    |


## Outputs

| Name                                                                                                                   | Description |
| ---------------------------------------------------------------------------------------------------------------------- | ----------- |
| <a name="output_azurerm_resource_group_name"></a> [azurerm\_resource\_group\_name](#output\_azurerm\_resource\_group\_name)                                        | Resource Group Name which got deployed         |
| <a name="output_azurerm_databricks_workspace_url"></a> [azurerm\_databricks\_workspace\_url](#output\_azurerm\_databricks\_workspace\_url)                      | Databricks Workspace URL which got deloyed         |
| <a name="output_databricks_token"></a> [databricks\_token](#output\_databricks\_token)                      | Databricks PAT Token          |
| <a name="output_azurerm_storage_account_name"></a> [azurerm\_storage\_account\_name](#output\_azurerm\_storage\_account\_name)                                        | ADLS Gen2 Storage Account which got deployed         |
| <a name="output_azurerm_storage_containers"></a> [azurerm\_storage\_containers](#output\_azurerm\_storage\_containers)                                             | Container named as `"dataset"` which got created         |
| <a name="output_azurerm_storage_containers_synapse"></a> [azurerm\_storage\_containers\_synapse](#output\_azurerm\_storage\_containers\_synapse) | Container named as `"synapse"` which got created and used by Synapse Workspace        |
| <a name="output_azurerm_storage_containers_synapsetemp"></a> [azurerm\_storage\_containers\_synapsetemp](#output\_azurerm\_storage\_containers\_synapsetemp) | Container named as `"synapsetemp"` which got created and used by Synapse Workspace for temporarily saving data during copy process from Azure Databricks to Azure Synapse       |
| <a name="output_azurerm_keyvault_name"></a> [azurerm\_keyvault\_name](#output\_azurerm\_keyvault\_name)                                       | Azure Key Vault Name which got deloyed        |
| <a name="output_azurerm_cosmosdb_endpoint"></a> [azurerm\_cosmosdb\_endpoint](#output\_azurerm\_cosmosdb\_endpoint)                                          | CosmosDB Endpoint Name which got deployed         |
| <a name="output_azurerm_cosmosdb_database"></a> [azurerm\_cosmosdb\_database](#output\_azurerm\_cosmosdb\_database)                                          | CosmosDB Database Name which got deployed, deault named as `"cosmos"`        |
| <a name="output_azurerm_eventhub_namespace"></a> [azurerm\_eventhub\_namespace](#output\_azurerm\_eventhub\_namespace)                                          | EventHub Namespace which got deployed         |
| <a name="output_azurerm_eventhub_entity_name"></a> [azurerm\_azurerm\_eventhub\_entity\_name](#output\_azurerm\_eventhub\_entity\_name)                                          | EventHub Entity which got deployed in EventHub Namespace         |
| <a name="output_azurerm_mssqlserver_name"></a> [azurerm\_mssqlserver\_name](#output\_azurerm\_mssqlserver\_name)                                          | Azure MS SQL Server which got deployed         |
| <a name="output_azurerm_mssqlserver_database_name"></a> [azurerm\_mssqlserver\_database\_name](#output\_azurerm\_mssqlserver\_database\_name)                                          | Azure MS SQL Server Database which got deployed                 |
| <a name="output_azurerm_mssqlserver_url"></a> [azurerm\_mssqlserver\_url](#output\_azurerm\_mssqlserver\_url)                                          | Azure MS SQL Server JDBC Connection URL                 |
| <a name="output_azurerm_mssqlserver_sql_user"></a> [azurerm\_mssqlserver\_sql\_user](#output\_azurerm\_mssqlserver\_sql\_user)                                          | Azure MS SQL Server User/Database User Name                 |
| <a name="output_azurerm_mssqlserver_sql_login_password"></a> [azurerm\_mssqlserver\_sql\_login\_password](#output\_azurerm\_mssqlserver\_sql\_login\_password)                                          | Azure MS SQL Server User/Database Password                 |
| <a name="output_azurerm_synapse_workspace_name"></a> [azurerm\_azurerm\_synapse\_workspace\_name](#output\_azurerm\_synapse\_workspace\_name)                                          | Azure Synapse Workspace Name         |
| <a name="output_azurerm_synapse_sql_pool_name"></a> [azurerm\_synapse\_sql\_pool\_name](#output\_azurerm\_synapse\_sql\_pool\_name)                                          | Azure Synapse SQL Pool Name                |
| <a name="output_azurerm_synapse_url"></a> [azurerm\_synapse\_url](#output\_azurerm\_synapse\_url)                                          | Azure Synapse JDBC Connection URL      |
| <a name="output_azurerm_synapse_user"></a> [azurerm\_synapse\_user](#output\_azurerm\_synapse\_user)                                          | Azure Synapse User/Database User Name                 |
| <a name="output_azurerm_synapse_password"></a> [azurerm\_synapse\_password](#output\_azurerm\_synapse\_password)                                          | Azure Synapse User/Database Password                 |

## Create Service Principal

This is not required but if we want to later test OAUTH Authentication to Azure Storage from Azure Databricks via Passthru Credentials then we need to create a Service Principal and save its details in Azure Key Vault.

Use below process to create a service princiapl.

1. Install Azure CLI
2. Open CMDlet and type
  
    `"az login"`
  
3. On successful login, set your subscription in which we need to create service principal

    `"az account set --subscription <SUBSCRIPTION NAME>"`
  
4. Run below command to create Service Principal

    `"az ad sp create-for-rbac --role="Contributor" --scopes="/subscriptions/<SUBSCRIPTION ID>"`

5. From the output note down
    a. appDisplayName
    b. appId
    c. name
    d. password
    e. tenant

6. Save this information in key vault
  
    **appId**    as **Azure-App-Registration-ClientID**
    
    **password** as **Azure-App-Registration-Client-Secret**
    
    **tenant**   as **Azure-Tenant-Id**
    
    
  
