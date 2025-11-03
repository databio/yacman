"""Test suite shared objects and setup"""

import os
from glob import glob

import pytest


@pytest.fixture
def data_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


@pytest.fixture
def cfg_file(data_path):
    return os.path.join(data_path, "conf.yaml")


@pytest.fixture
def full_cfg(data_path):
    """A config file with something in it"""
    return os.path.join(data_path, "full.yaml")


@pytest.fixture
def schema(data_path):
    return os.path.join(data_path, "conf_schema.yaml")


@pytest.fixture
def locked_cfg_file(data_path):
    return os.path.join(data_path, "lock.conf.yaml")


@pytest.fixture
def list_locks(data_path):
    return glob(os.path.join(data_path, "lock.*"))
