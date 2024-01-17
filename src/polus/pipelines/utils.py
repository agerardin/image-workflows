"""Utility functions."""

from typing import Any
from pathlib import Path
import os
from logging import Logger
import logging
import json
import yaml


def make_logger(file : str) -> Logger :
    logging.basicConfig(
        format="%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
    )
    POLUS_LOG = getattr(logging, os.environ.get("POLUS_LOG", "INFO"))
    logger = logging.getLogger(file)
    logger.setLevel(POLUS_LOG)
    return logger


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
