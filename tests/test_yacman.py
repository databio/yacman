import os

import pytest
from jsonschema.exceptions import ValidationError

import yacman
from yacman.const import FILEPATH_KEY, RO_KEY

from yacman import read_lock, write_lock
from ubiquerg import make_all_lock_paths, WRITE, READ


def get_temp_copy(cfg_template: str, tmp_cfg: str):
    """
    Copy a config file to a temp location and return the path to the temp file.
    This is useful for making sure the original file is not modified during tests,
    which could cause later tests to fail.
    """
    tmp_cfg = tmp_cfg / "tmp_config.yaml"
    print(f"Copied to temp config: {tmp_cfg}")
    with open(cfg_template, "r") as f:
        tmp_cfg.write_text(f.read())
    return str(tmp_cfg)


class TestWriting:
    def test_basic_write(self, cfg_file, tmp_path):
        tmp_cfg = get_temp_copy(cfg_file, tmp_path)
        ym = yacman.YAMLConfigManager.from_yaml_file(tmp_cfg)

        # Can't write outside a context manager
        with pytest.raises(OSError):
            ym.write()

        # File is locked when used in a context manager
        lock_paths = make_all_lock_paths(tmp_cfg)
        with write_lock(ym) as locked_ym:
            assert os.path.exists(lock_paths[WRITE])

    def test_write_creates_file(self, data_path, list_locks):
        ym = yacman.YAMLConfigManager(entries={})
        ym.write_copy(filepath=make_cfg_file_path("writeout.yaml", data_path))

        # Using .write with a filepath, outside of a context manager,
        # Doesn't lock the file.
        # import time
        # time.sleep(3)
        # assert os.path.exists(make_lock_path("writeout.yaml", data_path))

        assert os.path.exists(make_cfg_file_path("writeout.yaml", data_path))
        os.remove(make_cfg_file_path("writeout.yaml", data_path))

    def test_write(self, tmpdir):
        # Set up an empty temp file
        p = tmpdir.mkdir("sub").join("hello.yaml")
        p.write("{}")
        temp_path = str(p)
        ym = yacman.YAMLConfigManager.from_yaml_file(temp_path)
        rand_var = int.from_bytes(os.urandom(5), byteorder="big")
        ym["random_test_var"] = rand_var
        with write_lock(ym) as y:
            y.write()
        ym2 = yacman.YAMLConfigManager.from_yaml_file(temp_path)
        assert ym2["random_test_var"] == rand_var

    def test_rebase_only_on_locked(self, cfg_file):
        ym = yacman.YAMLConfigManager.from_yaml_file(cfg_file)

        with pytest.raises(OSError):
            ym.rebase()

        with read_lock(ym) as locked_ym:
            locked_ym.rebase()

    def test_read_lock(self, full_cfg, tmp_path):
        tmp_cfg = get_temp_copy(full_cfg, tmp_path)
        ym = yacman.YAMLConfigManager.from_yaml_file(tmp_cfg)
        ym2 = yacman.YAMLConfigManager.from_yaml_file(tmp_cfg)

        assert "var2" not in ym
        with write_lock(ym2) as ym:
            ym["var2"] = "val2"
            ym.write()

        with read_lock(ym) as locked_ym:
            print(locked_ym.locker.locked)
            locked_ym["var"] = "new"
            locked_ym.rebase()

        assert ym["var2"] == "val2"

        with write_lock(ym2) as locked_ym:
            del locked_ym["var2"]
            locked_ym.write()


class TestReadList:
    def test_read_list(self):
        ym = yacman.YAMLConfigManager.from_obj(["a", "b", "c"])
        print(ym.to_yaml())


def cleanup_locks(lcks):
    if lcks:
        [os.remove(l) for l in lcks]


def make_cfg_file_path(name, data_path):
    return os.path.join(data_path, name)


def make_lock_path(name, data_path):
    return os.path.join(data_path, yacman.LOCK_PREFIX + name)
