data azurerm_key_vault autoscription {
  name = "autoscription"
  resource_group_name = data.azurerm_resource_group.autoscription.name
}

data "azurerm_key_vault_secret" gitlab_container_registry_pat {
  key_vault_id = data.azurerm_key_vault.autoscription.id
  name         = "gitlab-container-regitry-pat"
}

data "azurerm_key_vault_secret" backend_logic_secret {
  key_vault_id = data.azurerm_key_vault.autoscription.id
  name         = "backend-logic-secret"
}

resource "azurerm_service_plan" "penicillin" {
  name                = "Penicillin-Service-Plan"
  resource_group_name = data.azurerm_resource_group.autoscription.name
  location            = data.azurerm_resource_group.autoscription.location
  os_type             = "Linux"
  sku_name            = "F1"
}

resource "azurerm_linux_web_app" "penicillin" {
  name                = "penicillin"
  resource_group_name = data.azurerm_resource_group.autoscription.name
  location            = data.azurerm_resource_group.autoscription.location
  service_plan_id     = azurerm_service_plan.penicillin.id
  app_settings = {
    APPINSIGHTS_INSTRUMENTATIONKEY =  azurerm_application_insights.autoscription.instrumentation_key
    APPLICATIONINSIGHTS_CONNECTION_STRING =  azurerm_application_insights.autoscription.connection_string
    AZURE_CLIENT_KEY= azuread_service_principal.backend_logic.application_id
    AZURE_CLIENT_SECRET= data.azurerm_key_vault_secret.backend_logic_secret.value
    AZURE_TENANT_ID= azuread_service_principal.backend_logic.application_tenant_id
    AZURE_ENDPOINT= data.azurerm_storage_account.customer_data.primary_table_endpoint
    ApplicationInsightsAgent_EXTENSION_VERSION = "~3"
    DOCKER_ENABLE_CI = true
  }
  https_only = true
  site_config {
    always_on = false
    health_check_path = "/healthcheck"
    application_stack {
      docker_image_name = "registry.gitlab.com/autoscription/autoscription/penicillin:latest"
      docker_registry_username = "VasilisSimeonidis"
      docker_registry_password = data.azurerm_key_vault_secret.gitlab_container_registry_pat.value
      docker_registry_url = "https://registry.gitlab.com/"
    }
  }
  tags = {environment="production"}
}


resource "azuread_application" "deployment_application" {
  display_name = "deployment_application"
}

resource "azuread_service_principal" "deployment_application" {
  application_id               = azuread_application.deployment_application.application_id
  app_role_assignment_required = false
}

resource "azurerm_role_assignment" "deployment_application" {
  scope                = azurerm_linux_web_app.penicillin.id
  role_definition_name = "Contributor"
  principal_id         = azuread_service_principal.deployment_application.object_id
}