resource "azurerm_storage_account" "example" {
  name                     = "${local.prefix}storage"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true
  account_kind             = "StorageV2"  
  tags                     = local.tags
}

//create a container named DataSet to copy few sample files
resource "azurerm_storage_container" "example" {
  name                  = "datasets"
  storage_account_name  = azurerm_storage_account.example.name
  container_access_type = "private"
}

//create a container named DataSet to copy few sample files
resource "azurerm_storage_container" "synapse" {
  name                  = "synapse"
  storage_account_name  = azurerm_storage_account.example.name
  container_access_type = "private"
}

//create a container named DataSet to copy few sample files
resource "azurerm_storage_container" "synapse_tmp" {
  name                  = "synapsetemp"
  storage_account_name  = azurerm_storage_account.example.name
  container_access_type = "private"
}



// Add Storage Name & SAS Key to KeyVault

resource "azurerm_key_vault_secret" "storagaccount" {
  name         = "storage-account-name"
  value        = azurerm_storage_account.example.name
  key_vault_id = azurerm_key_vault.example.id
}

resource "azurerm_key_vault_secret" "storageacesskey" {
  name         = "storage-access-key"
  value        = azurerm_storage_account.example.primary_access_key
  key_vault_id = azurerm_key_vault.example.id
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

                         

