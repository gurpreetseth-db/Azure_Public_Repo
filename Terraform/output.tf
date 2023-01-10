#Print Output

output "azurerm_resource_group_name" {
  //Name of the Resource Group
  value = azurerm_resource_group.example.name
}

output "azurerm_databricks_workspace_url" {
  //Databricks Workspce URL
  value = "https://${azurerm_databricks_workspace.example.workspace_url}/"
}

output "azurerm_storage_account_name" {
  // Storage Account Name
  value = azurerm_storage_account.example.name
}

output "azurerm_storage_containers" {
  // Storage Containers - dataset
  value = azurerm_storage_container.example.name
}

output "azurerm_storage_containers_synapse" {
  // Storage Containers - Synapse
  value = azurerm_storage_container.synapse.name
}

output "azurerm_storage_containers_synapsetemp" {
  // Storage Containers - Synapse Temp
  value = azurerm_storage_container.synapse_tmp.name
}


output "azurerm_keyvault_name" {
  // KeyVault Name
  value = azurerm_key_vault.example.name
}

output "azurerm_cosmosdb_endpoint" {
    // Cosmosdb Endpoint 
    value = azurerm_cosmosdb_account.db.endpoint
}

output "azurerm_cosmosdb_database" {
    // Cosmosdb Database
    value = azurerm_cosmosdb_sql_database.example.name
}


output "azurerm_eventhub_namespace" {
    // Eventhub Namespace
    value = azurerm_eventhub_namespace.example.name
}

output "azurerm_eventhub_entity_name" {
    // Event Hub Entity Name
    value = azurerm_eventhub.example.name
}


output "azurerm_mssqlserver_name" {
    // Azure SQL Server Name
    value = azurerm_mssql_server.example.name
}

output "azurerm_mssqlserver_database_name" {
    // Azure SQL Server Database Name
    value = azurerm_mssql_database.example.name
}

output "azurerm_mssqlserver_url" {
    // Azure SQL Server URL
    value = "jdbc:sqlserver://${azurerm_mssql_server.example.fully_qualified_domain_name};database=${azurerm_mssql_database.example.name};"
}

output "azurerm_mssqlserver_sql_user" {
    // Azure SQL Server User Name
    value = azurerm_mssql_server.example.administrator_login
    sensitive = true
}

output "azurerm_mssqlserver_sql_login_password" {
    // Azure SQL Server login
    value = azurerm_mssql_server.example.administrator_login_password
    sensitive = true
}

output "azurerm_synapse_workspace_name" {
    // Azure Synapse Workspace Name
    value = azurerm_synapse_workspace.example.name
}

output "azurerm_synapse_sql_pool_name" {
    // Azure Synapse SQL Pool Name
    value = azurerm_synapse_sql_pool.example.name
}

output "azurerm_synapse_url" {
    // Azure Synapse URL
    value = "jdbc:sqlserver://${azurerm_synapse_workspace.example.name}.sql.azuresynapse.net:1433;database=${azurerm_synapse_sql_pool.example.name};"
}


output "azurerm_synapse_user" {
    // Azure Synapse Login Name
    value = azurerm_synapse_workspace.example.sql_administrator_login
    sensitive = true
}

output "azurerm_synapse_password" {
    // Azure Synapse Login Password
    value = azurerm_synapse_workspace.example.sql_administrator_login_password
    sensitive = true
}
