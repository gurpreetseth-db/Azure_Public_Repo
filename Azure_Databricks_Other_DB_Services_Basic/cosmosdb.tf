
resource "azurerm_cosmosdb_account" "db" {
  name                = "${local.prefix}-cosmosdb-099"
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

resource "azurerm_cosmosdb_sql_database" "example" {
  name                = "cosmos"
  resource_group_name = azurerm_cosmosdb_account.db.resource_group_name
  account_name        = azurerm_cosmosdb_account.db.name
  throughput          = 400

}


