import flask
import flask_injector
from azure.data.tables import TableServiceClient
from azure.identity import ClientSecretCredential
from injector import Binder, Module, inject


class PenicillinModule(Module):  # type:ignore[misc]
    def configure(self, binder: Binder) -> None:
        binder.bind(TableServiceClient, to=self.table_service_client, scope=flask_injector.request)

    @inject  # type:ignore[misc]
    def table_service_client(self, config: flask.Config) -> TableServiceClient:
        client_key: str = config["AZURE_CLIENT_KEY"]
        client_secret: str = config["AZURE_CLIENT_SECRET"]
        tenant_id: str = config["AZURE_TENANT_ID"]
        endpoint: str = config["AZURE_ENDPOINT"]
        credentials = ClientSecretCredential(tenant_id, client_key, client_secret)
        return TableServiceClient(endpoint=endpoint, credential=credentials)
