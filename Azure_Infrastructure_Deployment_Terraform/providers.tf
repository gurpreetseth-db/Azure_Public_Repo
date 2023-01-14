# Configure the Microsoft Azure Provider
provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = false
    }
  }
}


provider "random" {
}

provider "databricks" {
  host = azurerm_databricks_workspace.example.workspace_url
}

provider "azuread" {
  tenant_id = data.azurerm_client_config.current.tenant_id
}