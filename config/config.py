import os

import yaml

from .errors import ConfigFileNotExist

PATH = "../config/"


class Config:
    def __init__(self, target, file="config.yml"):
        self.file = os.path.join(PATH, file)
        self.target = target

    def __enter__(self):
        try:
            return yaml.load(open(self.file), Loader=yaml.FullLoader)["AZURE"][self.target]
        except FileNotFoundError:
            raise ConfigFileNotExist(f"Please Check whether {self.file!r} exists or not")

    def __exit__(self, type, value, traceback):
        print(f"Loaded {self.target!r} in {self.file!r} file.")
