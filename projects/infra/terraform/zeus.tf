resource "azurerm_application_insights" "zeus" {
  name                = "zeus"
  location            = data.azurerm_resource_group.zeus-production.location
  resource_group_name = data.azurerm_resource_group.zeus-production.name
  application_type    = "other"
  workspace_id        = azurerm_log_analytics_workspace.zeus_production.id
  retention_in_days   = 30
  lifecycle {
    ignore_changes = []
  }
}

data azurerm_resource_group zeus-production {
  name = "zeus-production"
}

resource azurerm_log_analytics_workspace "zeus_production" {
  location            = data.azurerm_resource_group.zeus-production.location
  name                = "zeus-production"
  resource_group_name = data.azurerm_resource_group.zeus-production.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}