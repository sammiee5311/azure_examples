import os

from dotenv import load_dotenv

PATH = "../config/"
ENV_PATH = os.path.join(PATH, ".env")


def load_env():
    load_dotenv(dotenv_path=ENV_PATH)


def get_env(targets):
    targets = targets.split(",")

    return [os.environ[target] for target in targets]
