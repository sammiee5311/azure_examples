import sys

sys.path.append("..")

from azure_main import Azure, AzureBlob, AzureNames, AzureStorageManagement

STORAGE_ACCOUNT_NAME = "pythonazurestorage00"

names = AzureNames(
    resource_group="PythonAzureExample-Storage-rg",
    storage=STORAGE_ACCOUNT_NAME,
    container="blob-container-00",
    blob="sample-blob.txt",
)

azure_storage_sdk = AzureStorageManagement()
azure_blob_sdk = AzureBlob()

azure_storage = Azure(sdk=azure_storage_sdk, names=names)
azure_blob = Azure(sdk=azure_blob_sdk, names=names)

keys = azure_storage.sdk.get_keys()

conn_string = azure_storage.sdk.get_conn_string(keys)

azure_blob.sdk.set_conn_string(conn_string)
azure_blob.sdk.set_client()

with open("./files/sample-source.txt", "rb") as data:
    azure_blob.sdk.upload_blob(data)
