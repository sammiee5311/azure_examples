import sys

sys.path.append("..")

from azure_main import Azure, AzureNames, AzureResourceManagement

names = AzureNames(resource_group="PythonAzureExample-Storage-rg")

value = {"location": "centralus", "tags": {"environment": "test", "department": "tech"}}

azure_recourse_sdk = AzureResourceManagement()

azure_resource = Azure(sdk=azure_recourse_sdk, names=names)

# azure_resource.sdk.create(value)

azure_resource.sdk.print_resource_list()
