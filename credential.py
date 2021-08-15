from abc import ABC, abstractmethod

from azure.identity import AzureCliCredential, DefaultAzureCredential


class Credtential(ABC):
    @abstractmethod
    def get_credential(self):
        pass


class CliCredential(Credtential):
    def get_credential(self):
        return AzureCliCredential()


class DefaultCredential(Credtential):
    def get_credential(self):
        return DefaultAzureCredential()
