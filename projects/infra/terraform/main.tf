terraform {
  backend "azurerm" {
    subscription_id      = "1dbbb948-e494-41a6-905c-c3f2c732ed79"
    tenant_id            = "7d56198a-7d43-4d5d-8d6f-420187962fa2"
    resource_group_name  = "autoscription"
    storage_account_name = "stinfraautoscript001"
    container_name       = "tfstate"
    key                  = "production/autoscription"
  }
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = "1dbbb948-e494-41a6-905c-c3f2c732ed79"
  tenant_id       = "7d56198a-7d43-4d5d-8d6f-420187962fa2"
}

provider "azuread" {}

data azurerm_resource_group autoscription {
  name = "autoscription"
}

resource azurerm_log_analytics_workspace "autoscription_production" {
  location            = data.azurerm_resource_group.autoscription.location
  name                = "autoscription-production"
  resource_group_name = data.azurerm_resource_group.autoscription.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_application_insights" "autoscription" {
  name                = "autoscription"
  location            = data.azurerm_resource_group.autoscription.location
  resource_group_name = data.azurerm_resource_group.autoscription.name
  application_type    = "other"
  workspace_id        = azurerm_log_analytics_workspace.autoscription_production.id
  retention_in_days   = 30
  lifecycle {
    ignore_changes = []
  }
}

resource "azuread_application" "customer_email_notifier" {
  display_name = "customer_email_notifier"
}

resource "azuread_service_principal" "customer_email_notifier" {
  application_id               = azuread_application.customer_email_notifier.application_id
  app_role_assignment_required = false
}

data azurerm_storage_account "customer_data" {
    name = "stautoscriptionext002"
    resource_group_name = data.azurerm_resource_group.autoscription.name
}

resource "azurerm_role_assignment" "customer_data_reader" {
  scope                = data.azurerm_storage_account.customer_data.id
  role_definition_name = "Storage Table Data Reader"
  principal_id         = azuread_service_principal.customer_email_notifier.object_id
}

resource "azuread_application" "client_application" {
  display_name = "client_application"
}

resource "azuread_service_principal" "client_application" {
  application_id               = azuread_application.client_application.application_id
  app_role_assignment_required = false
}

resource "azurerm_role_assignment" "client_application" {
  scope                = data.azurerm_storage_account.customer_data.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azuread_service_principal.client_application.object_id
}


resource "azuread_application" "backend_logic" {
  display_name = "backend_logic"
}

resource "azuread_service_principal" "backend_logic" {
  application_id               = azuread_application.backend_logic.application_id
  app_role_assignment_required = false
}

resource "azurerm_role_assignment" "backend_logic" {
  scope                = data.azurerm_storage_account.customer_data.id
  role_definition_name = "Storage Blob Data Reader"
  principal_id         = azuread_service_principal.backend_logic.object_id
}

resource "azurerm_role_assignment" "backend_logic_writer" {
  scope                = data.azurerm_storage_account.customer_data.id
  role_definition_name = "Storage Table Data Contributor"
  principal_id         = azuread_service_principal.backend_logic.object_id
}