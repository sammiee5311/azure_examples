import sys

sys.path.append("..")

from azure_main import Azure
from azure_sdk import AzureResourceManagement
from config.config import load_env
from config.names import AzureNames

load_env()

names = AzureNames(resource_group="PythonAzureExample-rg")

value = {"location": "centralus", "tags": {"environment": "test", "department": "tech"}}

azure_recourse_sdk = AzureResourceManagement()

azure_resource = Azure(sdk=azure_recourse_sdk, names=names)

azure_resource.sdk.create_resoruce(value)

azure_resource.sdk.print_resource_list()
