resource "azurerm_storage_account" "example" {
  name                     = "${local.prefix}storage099"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true
  account_kind             = "StorageV2"  
  tags                     = local.tags
}


// COMMENT BELOW CODE 

// Add Sample File in Dataset folder
//resource "azurerm_storage_blob" "lendingclubcopy" {
//  for_each = fileset(path.module, "https://gurstorage.blob.core.windows.net/sampledatasets/lending_club/*")

//  name                   = trim(each.key, "lending_club/")
//  storage_account_name   = azurerm_storage_account.example.name
//  storage_container_name = azurerm_storage_container.example.name
//  type                   = "Block"
//  timeouts               {read = "10m"}  
//  source                 = each.key
//} 

                     

// Add Sample File in Dataset folder
//resource "azurerm_storage_blob" "example" {
//  name                   = "sample_data.json"
//  storage_account_name   = azurerm_storage_account.example.name
//  storage_container_name = azurerm_storage_container.example.name
//  type                   = "Block"
//  timeouts               {read = "10m"}  
//  source_uri             = "https://gurstorage.blob.core.windows.net/sampledatasets/sample_data.json"
//}                          

                         

