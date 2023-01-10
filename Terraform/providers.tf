# Configure the Microsoft Azure Provider
provider "azurerm" {
  features {}
}

provider "random" {
}

provider "databricks" {
  host = azurerm_databricks_workspace.example.workspace_url
}

provider "azuread" {
  tenant_id = data.azurerm_client_config.current.tenant_id
}