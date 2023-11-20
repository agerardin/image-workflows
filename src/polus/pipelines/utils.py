import json
import yaml
from pathlib import Path

def load_json(json_file :Path):
    with open(json_file, 'r') as file:
        return json.load(file)     

def load_yaml(yaml_file : Path):
        with open(yaml_file, 'r') as file:
            return yaml.safe_load(file)

def save_json(object, target : Path):
    with open(target, 'w') as json_file:
        json.dump(object, json_file, indent=4, sort_keys=True)

def save_yaml(object, target : Path):
    with open(target, 'w') as yaml_file:
        yaml.dump(object, yaml_file, indent=4, sort_keys=True)