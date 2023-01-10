

resource "azurerm_mssql_server" "example" {
  name                         = "${local.prefix}-001-sqlserver"
  resource_group_name          = azurerm_resource_group.example.name
  location                     = azurerm_resource_group.example.location
  version                      = "12.0"
  administrator_login          = "sqladmin"
  administrator_login_password = "P@ssword!!"
  tags                         = local.tags

}


resource "azurerm_mssql_database" "example" {
  name                = "${local.prefix}-001-sqlserver-db"
  server_id           = azurerm_mssql_server.example.id
  collation           = "SQL_Latin1_General_CP1_CI_AS"  
  tags                = local.tags
  sku_name            = "Basic"
  zone_redundant      = false
  read_scale          = false
}

// Add SQL Admin User & Password in Key Vault

resource "azurerm_key_vault_secret" "url" {
  name         = "sqlserver-jdbc-connection-string"
  value        =  "jdbc:sqlserver://${azurerm_mssql_server.example.fully_qualified_domain_name};database=${azurerm_mssql_database.example.name};"
  key_vault_id = azurerm_key_vault.example.id
}


resource "azurerm_key_vault_secret" "user" {
  name         = "sqlserver-db-user"
  value        = azurerm_mssql_server.example.administrator_login
  key_vault_id = azurerm_key_vault.example.id
}

resource "azurerm_key_vault_secret" "password" {
  name         = "sqlserver-db-password"
  value        = azurerm_mssql_server.example.administrator_login_password
  key_vault_id = azurerm_key_vault.example.id
}