from azure_sdk import AzureSDK
from config.names import AzureNames


class Azure:
    def __init__(self, sdk: AzureSDK, names: AzureNames):
        self.sdk = sdk
        self.sdk_set_names(names)

    def sdk_set_names(self, names):
        self.sdk.set_names(names)

    def __repr__(self):
        return f"Current SDK: {str(self.sdk)}"
