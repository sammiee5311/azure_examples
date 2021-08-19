import os

import yaml

from .errors import ConfigFileNotExist

PATH = "../config/"


class Config:
    def __init__(self, targets, file="config.yml"):
        self.file = os.path.join(PATH, file)
        self.targets = targets.split(",")

    def __enter__(self):
        try:
            data = yaml.load(open(self.file), Loader=yaml.FullLoader)
            result = []

            for target in self.targets:
                for key, value in data.items():
                    if target in value:
                        result.append(data[key][target])

            return result if len(result) > 1 else result[0]

        except FileNotFoundError:
            raise ConfigFileNotExist(f"Please Check whether {self.file!r} exists or not")

    def __exit__(self, type, value, traceback):
        print(f"Loaded {self.targets!r} in {self.file!r} file.")
