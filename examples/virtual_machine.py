import sys

sys.path.append("..")

from azure_main import Azure
from azure_sdk import (
    AzureComputeManagement,
    AzureNetworkManagement,
    AzureResourceManagement,
)
from config.config import load_env
from config.names import AzureNames

load_env()


LOCATION = "westus"
VM_NAME = "ExampleVM"
IP_CONFIG_NAME = "python-example-ip-config"
USERNAME = "azureuser"
PASSWORD = "ChangePa$$w0rd24"

vnet_value = {"location": LOCATION, "address_space": {"address_prefixes": ["10.0.0.0/16"]}}
subnet_value = {"address_prefix": "10.0.0.0/24"}
public_ip_address_value = {
    "location": LOCATION,
    "sku": {"name": "Standard"},
    "public_ip_allocation_method": "Static",
    "public_ip_address_version": "IPV4",
}
names = AzureNames(
    resource_group="PythonAzureExample-VM-rg",
    vnet="python-example-vnet",
    subnet="python-example-subnet",
    ip="python-example-ip",
    ip_config=IP_CONFIG_NAME,
    nic="python-example-nic",
    vm=VM_NAME,
)

azure_resource_sdk = AzureResourceManagement()
azure_network_sdk = AzureNetworkManagement()
azure_compute_sdk = AzureComputeManagement()

azure_resource = Azure(azure_resource_sdk, names)
azure_network = Azure(azure_network_sdk, names)
azure_compute = Azure(azure_compute_sdk, names)

azure_resource.sdk.create_resoruce({"location": LOCATION})

vent_result = azure_network.sdk.create_vnets(vnet_value)
subnet_result = azure_network.sdk.create_subnets(subnet_value)
ip_address_result = azure_network.sdk.create_public_ip_addresses(public_ip_address_value)

network_interface_value = {
    "location": LOCATION,
    "ip_configurations": [
        {"name": IP_CONFIG_NAME, "subnet": {"id": subnet_result.id}, "public_ip_address": {"id": ip_address_result.id}}
    ],
}

nic_result = azure_network.sdk.create_network_interfaces(network_interface_value)

vm_value = {
    "location": LOCATION,
    "storage_profile": {
        "image_reference": {
            "publisher": "Canonical",
            "offer": "UbuntuServer",
            "sku": "16.04.0-LTS",
            "version": "latest",
        }
    },
    "hardware_profile": {"vm_size": "Standard_DS1_v2"},
    "os_profile": {"computer_name": VM_NAME, "admin_username": USERNAME, "admin_password": PASSWORD},
    "network_profile": {
        "network_interfaces": [
            {
                "id": nic_result.id,
            }
        ]
    },
}

azure_compute.sdk.create_virtual_machines(vm_value)
