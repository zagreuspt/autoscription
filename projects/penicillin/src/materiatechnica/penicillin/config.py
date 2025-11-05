from distutils.util import strtobool
from os import environ


class Config:
    AZURE_CLIENT_KEY: str = environ.get("AZURE_CLIENT_KEY").__str__()
    AZURE_CLIENT_SECRET: str = environ.get("AZURE_CLIENT_SECRET").__str__()
    AZURE_TENANT_ID: str = environ.get("AZURE_TENANT_ID").__str__()
    AZURE_ENDPOINT: str = environ.get("AZURE_ENDPOINT").__str__()
    APPLICATIONINSIGHTS_CONNECTION_STRING: str = environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING").__str__()
    ENABLE_MONITORING: bool = strtobool(str(environ.get("ENABLE_MONITORING", default="true"))).__bool__()


class TestConfig(Config):
    AZURE_CLIENT_KEY: str = "824b5e48-a096-4983-a67f-7968512273fa"
    AZURE_TENANT_ID: str = "7d56198a-7d43-4d5d-8d6f-420187962fa2"
    AZURE_ENDPOINT: str = "https://stautoscriptionext002.table.core.windows.net/"
    APPLICATIONINSIGHTS_CONNECTION_STRING: str = (
        "InstrumentationKey=abd4a9ca-695d-4982-9378-6180576ed643;"
        "IngestionEndpoint=https://westeurope-5.in.applicationinsights.azure.com/;"
        "LiveEndpoint=https://westeurope.livediagnostics.monitor.azure.com/"
    )
    ENABLE_MONITORING: bool = False
