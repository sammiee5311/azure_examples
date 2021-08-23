from abc import ABC, abstractmethod

from azure.identity import AzureCliCredential, DefaultAzureCredential


class Credential(ABC):
    @abstractmethod
    def get_credential(self):
        pass


class CliCredential(Credential):
    def get_credential(self):
        return AzureCliCredential()


class DefaultCredential(Credential):
    def get_credential(self):
        return DefaultAzureCredential()
