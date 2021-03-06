import sys

sys.path.append("..")

from azure_main import Azure
from azure_sdk import AzureResourceManagement, AzureStorageManagement
from config.config import load_env
from config.errors import NameNotValid
from config.names import AzureNames

load_env()


LOCATION = "centralus"
STORAGE_ACCOUNT_NAME = f"pythonazurestorage00"

names = AzureNames(
    resource_group="PythonAzureExample-Storage-rg",
    storage=STORAGE_ACCOUNT_NAME,
    container="blob-container-00",
)

azure_resource_sdk = AzureResourceManagement()
azure_storage_sdk = AzureStorageManagement()

azure_resource = Azure(azure_resource_sdk, names)
azure_storage = Azure(azure_storage_sdk, names)

resource_value = {"location": LOCATION}
storage_value = {"location": LOCATION, "kind": "StorageV2", "sku": {"name": "Standard_LRS"}}

azure_resource.sdk.create_resoruce(resource_value)

if azure_storage.sdk.is_name_available_to_use():
    account_result = azure_storage.sdk.create_storage(value=storage_value)

    keys = azure_storage.sdk.get_keys()
    azure_storage.sdk.get_conn_string(keys)

    container = azure_storage.sdk.create_blob_containers({})
else:
    raise NameNotValid(f"{STORAGE_ACCOUNT_NAME!r} is not vaild name for a stroage account name")
