

resource "azurerm_mssql_server" "example" {
  name                         = "${local.prefix}-sqlserver-099"
  resource_group_name          = azurerm_resource_group.example.name
  location                     = azurerm_resource_group.example.location
  version                      = "12.0"
  administrator_login          = "sqladmin"
  administrator_login_password = "P@ssword!!"
  tags                         = local.tags

}


resource "azurerm_mssql_database" "example" {
  name                = "${local.prefix}-sqlserver--099-db"
  server_id           = azurerm_mssql_server.example.id
  collation           = "SQL_Latin1_General_CP1_CI_AS"  
  tags                = local.tags
  sku_name            = "Basic"
  zone_redundant      = false
  read_scale          = false
}
