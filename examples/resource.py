import sys

sys.path.append("..")

from azure_main import Azure
from azure_sdk import AzureResourceManagement
from config.names import AzureNames

names = AzureNames(resource_group="PythonAzureExample-rg")

value = {"location": "centralus", "tags": {"environment": "test", "department": "tech"}}

azure_recourse_sdk = AzureResourceManagement()

azure_resource = Azure(sdk=azure_recourse_sdk, names=names)

azure_resource.sdk.create(value)

azure_resource.sdk.print_resource_list()
