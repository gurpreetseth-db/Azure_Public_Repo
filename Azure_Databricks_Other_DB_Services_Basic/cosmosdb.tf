
resource "azurerm_cosmosdb_account" "db" {
  name                = "${local.prefix}-cosmosdb"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"
  tags                = local.tags

  enable_automatic_failover = false

  consistency_policy {
    consistency_level       = "Session"
    max_interval_in_seconds = 300
    max_staleness_prefix    = 100000
  }

  geo_location {
    location          = azurerm_resource_group.example.location
    failover_priority = 0
  }

}

// Add SQL Admin User & Password in Key Vault

resource "azurerm_key_vault_secret" "cosmosdbendpoint" {
  name         = "cosmosdb-account-endpoint"
  value        = azurerm_cosmosdb_account.db.endpoint
  key_vault_id = azurerm_key_vault.example.id
}

resource "azurerm_key_vault_secret" "cosmosdbaccountkey" {
  name         = "cosmosdb-accountkey"
  value        = azurerm_cosmosdb_account.db.primary_key
  key_vault_id = azurerm_key_vault.example.id
}

resource "azurerm_cosmosdb_sql_database" "example" {
  name                = "cosmos"
  resource_group_name = azurerm_cosmosdb_account.db.resource_group_name
  account_name        = azurerm_cosmosdb_account.db.name
  throughput          = 400
}