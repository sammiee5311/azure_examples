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
            data = yaml.load(open(self.file), Loader=yaml.FullLoader)

            for value, key in data.items():
                for name in key:
                    if self.target == name:
                        return data[value][name]

        except FileNotFoundError:
            raise ConfigFileNotExist(f"Please Check whether {self.file!r} exists or not")

    def __exit__(self, type, value, traceback):
        print(f"Loaded {self.target!r} in {self.file!r} file.")
