""" Test suite shared objects and setup """
import pytest
import os
from glob import glob


@pytest.fixture
def data_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


@pytest.fixture
def cfg_file(data_path):
    return os.path.join(data_path, "conf.yaml")


@pytest.fixture
def locked_cfg_file(data_path):
    return os.path.join(data_path, "lock.conf.yaml")


@pytest.fixture
def list_locks(data_path):
    print("getting locks in: {}".format(data_path))
    print(glob(os.path.join(data_path, "lock.*")))
    return glob(os.path.join(data_path, "lock.*"))

