
resource "azurerm_eventhub_namespace" "example" {
  name                = "${local.prefix}-eventhub-099"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  sku                 = "Basic"
  capacity            = 1
  tags                = local.tags
}

resource "azurerm_eventhub" "example" {
  name = "${local.prefix}-eventhub-databricks-099"
  namespace_name      = azurerm_eventhub_namespace.example.name
  resource_group_name = azurerm_resource_group.example.name   
  partition_count = 2
  message_retention = 1
  }

resource "azurerm_eventhub_authorization_rule" "example" {
  name                = "Default"
  namespace_name      = azurerm_eventhub_namespace.example.name
  eventhub_name       = azurerm_eventhub.example.name
  resource_group_name = azurerm_resource_group.example.name
  listen              = true
  send                = true
  manage              = true
}

