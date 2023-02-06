import os

import pytest
from jsonschema.exceptions import ValidationError

import yacman
from yacman.const import FILEPATH_KEY, IK, RO_KEY


class TestWriting:
    def test_basic_write(self, cfg_file, list_locks, data_path, locked_cfg_file):
        yacmap = yacman.YAMLConfigManager(filepath=cfg_file)

        # Can't write outside a context manager
        with pytest.raises(OSError):
            yacmap.write()

        # File is locked when used in a context manager
        with yacmap as _:
            assert os.path.exists(locked_cfg_file)

    def test_write_creates_file(self, data_path, list_locks):
        yacmap = yacman.YAMLConfigManager(entries={})
        yacmap.write_copy(filepath=make_cfg_file_path("writeout.yaml", data_path))

        # Using .write with a filepath, outside of a context manager,
        # Doesn't lock the file.
        # import time
        # time.sleep(3)
        # assert os.path.exists(make_lock_path("writeout.yaml", data_path))

        assert os.path.exists(make_cfg_file_path("writeout.yaml", data_path))
        os.remove(make_cfg_file_path("writeout.yaml", data_path))

    def test_rebase_only_on_locked(self, cfg_file):
        yacmap = yacman.YAMLConfigManager(filepath=cfg_file)

        with pytest.raises(OSError):
            yacmap.rebase()

        with yacmap as y:
            y.rebase()


def cleanup_locks(lcks):
    if lcks:
        [os.remove(l) for l in lcks]


def make_cfg_file_path(name, data_path):
    return os.path.join(data_path, name)


def make_lock_path(name, data_path):
    return os.path.join(data_path, yacman.LOCK_PREFIX + name)
