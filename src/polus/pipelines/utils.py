"""Utility functions to serialize/marshall data."""

import json
from pathlib import Path
from typing import Any

import yaml


def load_json(json_file: Path) -> Any:  # noqa
    """Load json file."""
    with Path.open(json_file) as file:
        return json.load(file)


def load_yaml(yaml_file: Path) -> Any:  # noqa
    """Load yaml file."""
    with Path.open(yaml_file) as file:
        return yaml.safe_load(file)


def save_json(data: Any, target: Path) -> None:  # noqa
    """Save json file."""
    with Path.open(target, "w") as json_file:
        json.dump(data, json_file, indent=4, sort_keys=True)


def save_yaml(data: Any, target: Path) -> None:  # noqa
    """Save json file."""
    with Path.open(target, "w") as yaml_file:
        yaml.dump(data, yaml_file, indent=4, sort_keys=True)
