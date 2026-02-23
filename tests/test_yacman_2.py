import os

import pytest

import yacman
from ubiquerg import read_lock, write_lock


class TestWriting:
    def test_basic_write(self, cfg_file, data_path):
        yacmap = yacman.YAMLConfigManager.from_yaml_file(cfg_file)

        # Can't write outside a write lock
        with pytest.raises(OSError):
            yacmap.write()

        # Works inside a write_lock context manager
        with write_lock(yacmap) as _:
            yacmap.write()

    def test_write_creates_file(self, data_path):
        yacmap = yacman.YAMLConfigManager(entries={})
        yacmap.write_copy(filepath=make_cfg_file_path("writeout.yaml", data_path))
        assert os.path.exists(make_cfg_file_path("writeout.yaml", data_path))
        os.remove(make_cfg_file_path("writeout.yaml", data_path))

    def test_rebase_only_on_locked(self, cfg_file):
        yacmap = yacman.YAMLConfigManager.from_yaml_file(cfg_file)

        with pytest.raises(OSError):
            yacmap.rebase()

        with read_lock(yacmap) as y:
            y.rebase()


class TestReadList:
    def test_read_list(self):
        yacmap = yacman.YAMLConfigManager(entries=["a", "b", "c"])
        print(yacmap.to_yaml())


def make_cfg_file_path(name, data_path):
    return os.path.join(data_path, name)
