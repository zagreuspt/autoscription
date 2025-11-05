resource "azuread_group" "Engineering" {
  display_name = "Engineering"
  security_enabled = true
}

data "azuread_user" "petros_bibiris" {
  user_principal_name = "petros.bibiris@materiatechnica.com"
}

resource "azuread_group_member" "petros_bibiris" {
  group_object_id  = azuread_group.Engineering.object_id
  member_object_id = data.azuread_user.petros_bibiris.object_id
}

resource "azurerm_role_assignment" "application_insights_reader" {
 scope                = azurerm_application_insights.zeus.id
 role_definition_name = "Reader"
 principal_id         = azuread_group.Engineering.object_id
}

data azurerm_storage_account infra_storage {
  resource_group_name = "autoscription"
  name = "stinfraautoscript001"
}

resource "azurerm_role_assignment" "infra_storage_contributor" {
 scope                = data.azurerm_storage_account.infra_storage.id
 role_definition_name = "Contributor"
 principal_id         = azuread_group.Engineering.object_id
}