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

resource "databricks_cluster" "Single_AutoScale" {
  cluster_name            = var.clustername
  spark_version           = var.spark_version
  node_type_id            = var.node_type_id
  data_security_mode      = var.access_mode
  single_user_name        =  var.single_user_access
  autotermination_minutes = var.autotermination_minutes
  autoscale {
    min_workers = 1
    max_workers = 3
  }
}

// Install Librararies
resource "databricks_library" "eventhub" {
  cluster_id = databricks_cluster.Single_AutoScale.id
  maven {
    coordinates = "com.microsoft.azure:azure-eventhubs-spark_2.12:2.3.18"
  }  
}

resource "databricks_library" "mssql" {
  cluster_id = databricks_cluster.Single_AutoScale.id
  maven {
    coordinates = "com.microsoft.azure:spark-mssql-connector_2.12:1.2.0"
  }  
}

resource "databricks_library" "cosmos" {
  cluster_id = databricks_cluster.Single_AutoScale.id
  maven {
    coordinates = "com.azure.cosmos.spark:azure-cosmos-spark_3-1_2-12:4.15.0"
  }  
}



//Create Secre Scope and Connect with Azure Key Vault
resource "databricks_secret_scope" "kv" {
  name = "Databricks-KeyVault-Scope"
  initial_manage_principal = "users"

  keyvault_metadata {
    resource_id = var.keyvault_id
    dns_name    = var.keyvault_url
  }

}
// Completed //

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
  key_vault_id = var.keyvault_id
}


// output token for other modules
output "databricks_token" {
  value     = databricks_token.pat.token_value
  sensitive = true
}
// Completed //