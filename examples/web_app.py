import sys

sys.path.append("..")

from azure_main import Azure
from azure_sdk import AzureResourceManagement, AzureWebSiteManagement
from config.names import AzureNames

REPO_URL = ""
LOCATION = "centralus"

names = AzureNames(
    resource_group="PythonAzureExample-WebApp-rg",
    web_app="PythonAzureExample-WebApp-00",
    service_plan="PythonAzureExample-WebApp-plan",
)

azure_resource_sdk = AzureResourceManagement()
azure_web_sdk = AzureWebSiteManagement()

azure_resource = Azure(azure_resource_sdk, names)
azure_web = Azure(azure_web_sdk, names)

azure_resource.sdk.create_resoruce({"location": LOCATION})

poller = azure_web.sdk.create_app_service_plans({"location": LOCATION, "reserved": True, "sku": {"name": "B1"}})

plan_result = poller.result()

print(f"Provisioned App Service plan {plan_result.name}")

poller = azure_web.sdk.create_web_apps(
    {"location": LOCATION, "server_farm_id": plan_result.id, "site_config": {"linux_fx_version": "python|3.8"}},
)

web_app_result = poller.result()

print(f"Provisioned web app {web_app_result.name} at {web_app_result.default_host_name}")

poller = azure_web.sdk.create_source_control({"location": "GitHub", "repo_url": REPO_URL, "branch": "master"})

sc_result = poller.result()

print(f"Set source control on web app to {sc_result.branch} branch of {sc_result.repo_url}")
