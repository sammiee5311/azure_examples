import sys

sys.path.append("..")

from azure_main import Azure
from azure_sdk import AzureSecret
from config.config import load_env
from config.names import AzureNames

load_env()

names = AzureNames(resource_group="KeyValutTest")

azure_key_vault_sdk = AzureSecret()

azure_key_vault = Azure(azure_key_vault_sdk, names)

azure_key_vault.sdk.set_secret_key_value("woooow", 1234)

secret = azure_key_vault.sdk.get_secret_value("woooow")

azure_key_vault.sdk.delete_secret_key("woooow")
