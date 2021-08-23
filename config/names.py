from dataclasses import dataclass
from typing import Optional


@dataclass
class AzureNames:
    resource_group: str = "Resource Group"
    blob: Optional[str] = None
    container: Optional[str] = None
    storage: Optional[str] = None
    service_plan: Optional[str] = None
    web_app: Optional[str] = None
    rule: Optional[str] = None
    vnet: Optional[str] = None
    subnet: Optional[str] = None
    ip: Optional[str] = None
    ip_config: Optional[str] = None
    nic: Optional[str] = None
    vm: Optional[str] = None
