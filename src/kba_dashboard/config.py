from pyaml_env import parse_config
from pathlib import Path
import glob
from .models.pydantic_models import Product

def find_config_file():
    config_files = glob.glob("**/config.yml", recursive=True)

    for match in config_files:
        config_path = Path(match)
        if config_path.is_file():
            print(f"Trying to load config from path '{str(config_path)}' ...")
            return config_path
    raise FileNotFoundError(
        "Could not find config.yml"
    )

def load_config():
    config_path = find_config_file()
    parsed_config = parse_config(config_path)
    print(f"Successfully loaded config file from '{config_path}'")

    return parsed_config


