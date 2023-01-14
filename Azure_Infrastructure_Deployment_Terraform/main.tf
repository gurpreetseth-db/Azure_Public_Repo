terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">=3.10.0"
    }
    databricks = {
      source  = "databricks/databricks"
      version = ">=0.5.1"
    }
  }
}

resource "random_string" "naming" {
  special = false
  upper   = false
  length  = 6
}

resource "azurerm_resource_group" "example" {
  name     = "${substr(lower(var.name),0,3)}-demo-rg"
  location = var.rglocation
}

locals {
  // dltp - databricks labs terraform provider
  prefix   = substr(lower(var.name),0,3)
  location = var.rglocation
  dbfsname = "${substr(lower(var.name),0,3)}dbfs" // dbfs name must not have special chars

  // tags that are propagated down to all resources
  tags = {
    Environment = "Testing"
    Owner       = var.name
    Email       = var.email
  }
}


data "databricks_spark_version" "latest_lts" {
  long_term_support = true
}


module "auto_scaling_cluster_example" {
  source                  = "./modules/autoscaling_cluster"
  clustername             = "Single User Autoscaling"
  spark_version           = "10.4.x-scala2.12" #data.databricks_spark_version.latest_lts.id
  node_type_id            = var.node_type
  autotermination_minutes = var.global_auto_termination_minute
  access_mode             = "LEGACY_SINGLE_USER_STANDARD"
  single_user_access      = var.email
  keyvault_id             = azurerm_key_vault.example.id
  keyvault_url            = azurerm_key_vault.example.vault_uri
  tenant_id               = data.azurerm_client_config.current.tenant_id

depends_on = [azurerm_key_vault.example]
}


//Cosmosdb LTS 9.1


module "auto_scaling_cluster_cosmosdb" {
  source                  = "./modules/autoscaling_cluster"
  clustername             = "Single User - Cosmosdb"
  spark_version           = "9.1.x-scala2.12"
  node_type_id            = var.node_type
  autotermination_minutes = var.global_auto_termination_minute
  access_mode             = "LEGACY_SINGLE_USER_STANDARD"
  single_user_access      = var.email
  keyvault_id             = azurerm_key_vault.example.id
  keyvault_url            = azurerm_key_vault.example.vault_uri
  tenant_id               = data.azurerm_client_config.current.tenant_id

depends_on = [azurerm_key_vault.example]
}


// Add SQL Admin User & Password in Key Vault

resource "azurerm_key_vault_secret" "cosmosdbendpoint" {
  name         = "cosmosdb-account-endpoint"
  value        = azurerm_cosmosdb_account.db.endpoint
  key_vault_id = azurerm_key_vault.example.id
  depends_on = [azurerm_cosmosdb_sql_database.example]
}

resource "azurerm_key_vault_secret" "cosmosdbaccountkey" {
  name         = "cosmosdb-accountkey"
  value        = azurerm_cosmosdb_account.db.primary_key
  key_vault_id = azurerm_key_vault.example.id
  depends_on = [azurerm_cosmosdb_sql_database.example]  
}


// Add Primary Connection To KeyVault For Azure EventHub created above
resource "azurerm_key_vault_secret" "eventhubstring" {
  name         = "eventhub-databricks-sas-connection-string"
  value        = azurerm_eventhub_authorization_rule.example.primary_connection_string
  key_vault_id = azurerm_key_vault.example.id
  depends_on = [azurerm_eventhub.example]    
}


// Add SQL Admin User & Password in Key Vault

resource "azurerm_key_vault_secret" "url" {
  name         = "sqlserver-jdbc-connection-string"
  value        =  "jdbc:sqlserver://${azurerm_mssql_server.example.fully_qualified_domain_name};database=${azurerm_mssql_database.example.name};"
  key_vault_id = azurerm_key_vault.example.id
  depends_on = [azurerm_mssql_database.example]      
}


resource "azurerm_key_vault_secret" "user" {
  name         = "sqlserver-db-user"
  value        = azurerm_mssql_server.example.administrator_login
  key_vault_id = azurerm_key_vault.example.id
  depends_on = [azurerm_mssql_database.example]    
}

resource "azurerm_key_vault_secret" "password" {
  name         = "sqlserver-db-password"
  value        = azurerm_mssql_server.example.administrator_login_password
  key_vault_id = azurerm_key_vault.example.id
  depends_on = [azurerm_mssql_database.example]    
}


//create a container named DataSet to copy few sample files
resource "azurerm_storage_container" "example" {
  name                  = "datasets"
  storage_account_name  = azurerm_storage_account.example.name
  container_access_type = "private"
}

//create a container named DataSet to copy few sample files
resource "azurerm_storage_container" "synapse" {
  name                  = "synapse"
  storage_account_name  = azurerm_storage_account.example.name
  container_access_type = "private"
}

//create a container named DataSet to copy few sample files
resource "azurerm_storage_container" "synapse_tmp" {
  name                  = "synapsetemp"
  storage_account_name  = azurerm_storage_account.example.name
  container_access_type = "private"
}



// Add Storage Name & SAS Key to KeyVault

resource "azurerm_key_vault_secret" "storagaccount" {
  name         = "storage-account-name"
  value        = azurerm_storage_account.example.name
  key_vault_id = azurerm_key_vault.example.id
  depends_on = [azurerm_storage_account.example]    
}

resource "azurerm_key_vault_secret" "storageacesskey" {
  name         = "storage-access-key"
  value        = azurerm_storage_account.example.primary_access_key
  key_vault_id = azurerm_key_vault.example.id
  depends_on = [azurerm_storage_account.example]     
}


// Add Synapse Admin User & Password in Key Vault

resource "azurerm_key_vault_secret" "synapseurl" {
  name         = "synapse-jdbc-connection-string"
  value        =  "jdbc:sqlserver://${azurerm_synapse_workspace.example.name}.sql.azuresynapse.net:1433;database=${azurerm_synapse_sql_pool.example.name};"
  key_vault_id = azurerm_key_vault.example.id
  depends_on = [azurerm_synapse_sql_pool.example]     
}


resource "azurerm_key_vault_secret" "synapseuser" {
  name         = "synapse-db-user"
  value        = azurerm_synapse_workspace.example.sql_administrator_login
  key_vault_id = azurerm_key_vault.example.id
  depends_on = [azurerm_synapse_sql_pool.example]       
}

resource "azurerm_key_vault_secret" "synapsepassword" {
  name         = "synapse-db-password"
  value        = azurerm_synapse_workspace.example.sql_administrator_login_password
  key_vault_id = azurerm_key_vault.example.id
  depends_on = [azurerm_synapse_sql_pool.example]       
}

// create PAT token to provision entities within workspace
resource "databricks_token" "pat" {
  provider = databricks
  comment  = "Terraform Provisioning"
  // 100 day token
  lifetime_seconds = 8640000
}

// Add token to key vault
resource "azurerm_key_vault_secret" "databricks_pat_token" {
  name         = "databricks-pat-token"
  value        = databricks_token.pat.token_value
  key_vault_id = azurerm_key_vault.example.id
}



//Create Secre Scope and Connect with Azure Key Vault
resource "databricks_secret_scope" "kv" {
  name = "Databricks-KeyVault-Scope"
  initial_manage_principal = "users"

  keyvault_metadata {
    resource_id = azurerm_key_vault.example.id
    dns_name    = azurerm_key_vault.example.vault_uri
  }

}