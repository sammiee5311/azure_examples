from abc import ABC, abstractmethod

from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.storage.blob import BlobClient

from config.config import Config
from config.names import AzureNames
from credential import CliCredential, Credtential


def get_config(name):
    with Config(name) as result:
        return result


class AzureSDK(ABC):

    names: AzureNames = None

    def set_names(self, names: AzureNames):
        self.names = names

    def get_names(self, **kwargs):
        names = []

        for key, value in kwargs.items():
            if value:
                names.append(value)
            else:
                names.append(getattr(self.names, key))

        return names


class AzureResourceManagement(AzureSDK):
    def __init__(self, credential: Credtential = CliCredential()):
        self.credential = credential.get_credential()
        self.client = ResourceManagementClient(self.credential, get_config("SUBSCRIPTION_ID"))

    def __str__(self):
        return "ResourceManagement"

    def get_resource_list(self, resource_group=None, expand="createdTime,changedTime"):
        names = self.get_names(resource_group=resource_group)
        return self.client.resources.list_by_resource_group(*names, expand=expand)

    def create(self, value, resource_group=None):
        names = self.get_names(resource_group=resource_group)
        result = self.client.resource_groups.create_or_update(*names, value)

        print(f"Provisioned resource group {result.name!r} in the {result.location!r} region")

        if "tags" in value:
            print(f"Updated resource group {result.name!r} with tags: {list(value['tags'].keys())}")

    def print_group_list(self):
        resource_group = self.client.resource_groups.list()
        column_width = 40

        print("Resource Group".ljust(column_width) + "Location")
        print("-" * (column_width * 2))

        for group in list(resource_group):
            print(f"{group.name:<{column_width}}{group.location}")

    def print_resource_list(self, resource_group=None):
        resource_list = self.get_resource_list(resource_group)
        column_width = 36

        print(
            "Resource".ljust(column_width)
            + "Type".ljust(column_width)
            + "Create date".ljust(column_width)
            + "Change date".ljust(column_width)
        )
        print("-" * (column_width * 4))

        for resource in resource_list:
            print(
                f"{resource.name:<{column_width}}{resource.type:<{column_width}}"
                f"{str(resource.created_time):<{column_width}}{str(resource.changed_time):<{column_width}}"
            )


class AzureStorageManagement(AzureSDK):
    def __init__(self, credential: Credtential = CliCredential()):
        self.credential = credential.get_credential()
        self.client = StorageManagementClient(self.credential, get_config("SUBSCRIPTION_ID"))
        self.conn_string = None

    def __str__(self):
        return "StorageManagement"

    def is_name_available_to_use(self):
        return self.client.storage_accounts.check_name_availability({"name": self.names.storage}).name_available

    def create_storage(self, value, resource_group=None, storage=None):
        names = self.get_names(resource_group=resource_group, storage=storage)
        return self.client.storage_accounts.begin_create(*names, value)

    def create_blob_containers(self, value, resource_group=None, storage=None, container=None):
        names = self.get_names(resource_group=resource_group, storage=storage, container=container)
        return self.client.blob_containers.create(*names, value)

    def get_keys(self, resource_group=None, show=True):
        names = self.get_names(resource_group=resource_group)
        keys = self.client.storage_accounts.list_keys(*names, self.names.storage)

        if show:
            print(f"Primary key for storage account: {keys.keys[0].value}")

        return keys

    def get_conn_string(self, keys, storage=None):
        storage = self.get_names(storage=storage)
        conn_string = f"DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName={storage[0]};AccountKey={keys.keys[0].value}"

        print(f"Connection string: {conn_string}")

        return conn_string


class AzureBlob(AzureSDK):
    def __init__(self, conn_string=None, credential: Credtential = CliCredential()):
        self.credential = credential.get_credential()
        self.conn_string = conn_string
        self.client = None

    def __str__(self):
        return "blob"

    def set_conn_string(self, conn_string):
        self.conn_string = conn_string

    def set_client(self, container=None, blob=None):
        names = self.get_names(container=container, blob=blob)
        self.client = BlobClient.from_connection_string(self.conn_string, *names)

    def upload_blob(self, data):
        self.client.upload_blob(data)


class AzureWebSiteManagement(AzureSDK):
    def __init__(self, credential: Credtential = CliCredential()):
        self.credential = credential.get_credential()
        self.client = WebSiteManagementClient(self.credential, get_config("SUBSCRIPTION_ID"))

    def __str__(self):
        return "WebSiteManagement"

    def create_app_service_plans(self, value, resource_group=None, service_plan=None):
        names = self.get_names(resource_group=resource_group, service_plan=service_plan)
        return self.client.app_service_plans.begin_create_or_update(*names, value)

    def create_web_apps(self, value, resource_group=None, web_app=None):
        names = self.get_names(resource_group=resource_group, web_app=web_app)
        return self.client.web_apps.begin_create_or_update(*names, value)

    def create_source_control(self, value, resource_group=None, web_app=None):
        names = self.get_names(resource_group=resource_group, web_app=web_app)
        return self.client.web_apps.begin_create_or_update_source_control(*names, value)
