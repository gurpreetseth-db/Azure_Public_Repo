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