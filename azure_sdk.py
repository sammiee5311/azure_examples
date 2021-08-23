from abc import ABC, abstractmethod

import mysql.connector
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.rdbms.mysql import MySQLManagementClient
from azure.mgmt.rdbms.mysql.models import (
    ServerForCreate,
    ServerPropertiesForDefaultCreate,
    ServerVersion,
)
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.storage.blob import BlobClient

from config.config import Config
from config.names import AzureNames
from credential import CliCredential, Credential


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


class AzureDatabaseManagement(AzureSDK):
    pass


class AzureResourceManagement(AzureSDK):
    def __init__(self, credential: Credential = CliCredential()):
        self.credential = credential.get_credential()
        self.client = ResourceManagementClient(self.credential, get_config("SUBSCRIPTION_ID"))

    def __str__(self):
        return "ResourceManagement"

    def get_resource_list(self, resource_group=None, expand="createdTime,changedTime"):
        names = self.get_names(resource_group=resource_group)
        return self.client.resources.list_by_resource_group(*names, expand=expand)

    def create_resoruce(self, value, resource_group=None):
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
    def __init__(self, credential: Credential = CliCredential()):
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
    def __init__(self, conn_string=None, credential: Credential = CliCredential()):
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
    def __init__(self, credential: Credential = CliCredential()):
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


class AzureMySQLManagement(AzureDatabaseManagement):
    def __init__(self, credential: Credential = CliCredential()):
        self.credential = credential.get_credential()
        self.client = MySQLManagementClient(self.credential, get_config("SUBSCRIPTION_ID"))
        self.server_name, self.admin_name, self.admin_password, self.ip_address, self.name, self.port = get_config(
            "SEVER_NAME,ADMIN_NAME,ADMIN_PASSWORD,PUBLIC_IP_ADDRESS,NAME,PORT"
        )

    def create_servers(self, location, version, resource_group=None):
        names = self.get_names(resource_group=resource_group)
        poller = self.client.servers.begin_create(
            *names,
            self.server_name,
            ServerForCreate(
                location=location,
                properties=ServerPropertiesForDefaultCreate(
                    administrator_login=self.admin_name,
                    administrator_login_password=self.admin_password,
                    version=getattr(ServerVersion, version),
                ),
            ),
        )
        return poller.result()

    def create_firewall_rules(self, rule, resource_group=None):
        names = self.get_names(resource_group=resource_group)
        poller = self.client.firewall_rules.begin_create_or_update(
            *names, self.server_name, rule, {"start_ip_address": self.ip_address, "end_ip_address": self.ip_address}
        )

        return poller.result()

    def create_database(self, value, resource_group=None):
        names = self.get_names(resource_group=resource_group)
        poller = self.client.databases.begin_create_or_update(*names, self.server_name, self.name, value)

        return poller.result()

    def connect_to_database(self):
        connection = mysql.connector.connect(
            user=f"{self.admin_name}@{self.server_name}",
            password=self.admin_password,
            host=f"{self.server_name}.mysql.database.azure.com",
            port=self.port,
            database=self.name,
            ssl_ca="../files/BaltimoreCyberTrustRoot.crt.pem",
        )

        return connection


class AzureNetworkManagement(AzureSDK):
    def __init__(self, credential: Credential = CliCredential()):
        self.credential = credential.get_credential()
        self.client = NetworkManagementClient(self.credential, get_config("SUBSCRIPTION_ID"))

    def create_vnets(self, value, resource_group=None, vnet=None):
        names = self.get_names(resource_group=resource_group, vnet=vnet)
        poller = self.client.virtual_networks.begin_create_or_update(*names, value)
        vnet_result = poller.result()

        print(
            f"Provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}"
        )

        return vnet_result

    def create_subnets(self, value, resource_group=None, vnet=None, subnet=None):
        names = self.get_names(resource_group=resource_group, vnet=vnet, subnet=subnet)
        poller = self.client.subnets.begin_create_or_update(*names, value)
        subnet_result = poller.result()

        print(f"Provisioned virtual subnet {subnet_result.name} with address prefix {subnet_result.address_prefix}")

        return subnet_result

    def create_public_ip_addresses(self, value, resource_group=None, ip=None):
        names = self.get_names(resource_group=resource_group, ip=ip)
        poller = self.client.public_ip_addresses.begin_create_or_update(*names, value)
        ip_address_result = poller.result()

        print(f"Provisioned public IP address {ip_address_result.name} with address {ip_address_result.ip_address}")

        return ip_address_result

    def create_network_interfaces(self, value, resource_group=None, nic=None):
        names = self.get_names(resource_group=resource_group, nic=nic)
        poller = self.client.network_interfaces.begin_create_or_update(*names, value)
        nic_result = poller.result()

        print(f"Provisioned network interface client {nic_result.name}")

        return nic_result


class AzureComputeManagement(AzureSDK):
    def __init__(self, credential: Credential = CliCredential()):
        self.credential = credential.get_credential()
        self.client = ComputeManagementClient(self.credential, get_config("SUBSCRIPTION_ID"))

    def create_virtual_machines(self, value, resource_group=None, vm=None):
        names = self.get_names(resource_group=resource_group, vm=vm)
        poller = self.client.virtual_machines.begin_create_or_update(*names, value)
        vm_result = poller.result()

        print(f"Provisioned virtual machine {vm_result.name}")

        return vm_result
