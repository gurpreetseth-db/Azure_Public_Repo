
//Managed Resource Group For Synapse
//resource "azurerm_resource_group" "synapsemanaged" {
//  name     = "${substr(lower(var.name),0,3)}-synapse-rg"
//  location = var.rglocation
//}

//File System (Created in Storge Account we created ealier)

//resource "azurerm_storage_data_lake_gen2_filesystem" "example" {
//  name               = "synapse"
//  storage_account_id = azurerm_storage_account.example.id
//}

resource "azurerm_synapse_workspace" "example" {
  name                                 = "${local.prefix}-synapse-099"
  resource_group_name                  = azurerm_resource_group.example.name
  managed_resource_group_name          = "${substr(lower(var.name),0,3)}-synapse-rg"
  location                             = azurerm_resource_group.example.location
  //storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.example.id
  storage_data_lake_gen2_filesystem_id = "https://${azurerm_storage_account.example.name}.dfs.core.windows.net/synapse"
  sql_administrator_login              = "sqladmin"
  sql_administrator_login_password     = "P@ssword!!!"
  tags                                 = local.tags
  public_network_access_enabled        = true

 // aad_admin {
 //   login     = var.email
 //   object_id            = "00000000-0000-0000-0000-000000000000"
 //   tenant_id            = "00000000-0000-0000-0000-000000000000"    
 // }

  identity {
    type = "SystemAssigned"
  }
}


resource "azurerm_synapse_workspace_aad_admin" "example" {
  synapse_workspace_id = azurerm_synapse_workspace.example.id
  login                = var.email
  object_id            = data.azurerm_client_config.current.object_id
  tenant_id            = data.azurerm_client_config.current.tenant_id
}

resource "azurerm_synapse_sql_pool" "example" {
  name                 = "${substr(lower(var.name),0,3)}sqlpool"
  synapse_workspace_id = azurerm_synapse_workspace.example.id
  sku_name             = "DW100c"
  create_mode          = "Default"
}


resource "azurerm_synapse_firewall_rule" "example" {
  name                 = "AllowAll"
  synapse_workspace_id = azurerm_synapse_workspace.example.id
  start_ip_address     = "0.0.0.0"
  end_ip_address       = "255.255.255.255"
}
