import pytest
import yacman
import os


class TestWriting:
    def test_basic_write(self, cfg_file, list_locks, data_path, locked_cfg_file):
        yacmap = yacman.YacAttMap(filepath=cfg_file, writable=True)
        assert os.path.exists(locked_cfg_file)
        yacmap.write()

    def test_write_creates_file(self, data_path, list_locks):
        with pytest.warns(UserWarning):
            yacmap = yacman.YacAttMap(entries={}, writable=True)
        yacmap.write(filepath=make_cfg_file_path("writeout.yaml", data_path))
        assert os.path.exists(make_lock_path("writeout.yaml", data_path))
        assert os.path.exists(make_cfg_file_path("writeout.yaml", data_path))
        os.remove(make_cfg_file_path("writeout.yaml", data_path))

    @pytest.mark.parametrize(["name", "entry"], [("updated.yaml", "update"), ("updated1.yaml", "update1")])
    def test_entries_update(self, name, data_path, entry):
        filepath = make_cfg_file_path(name, data_path)
        yacmap = yacman.YacAttMap(entries={})
        yacmap.test = entry
        yacmap.write(filepath=filepath)
        yacmapin = yacman.YacAttMap(filepath=filepath, writable=False)
        assert(yacmapin.test == entry)
        os.remove(filepath)

    @pytest.mark.parametrize("name", ["test.yaml", "test1.yaml"])
    def test_warn_on_write_when_not_locked(self, name, data_path, cfg_file):
        yacmap = yacman.YacAttMap(entries={})
        filename = make_cfg_file_path(name, data_path)
        f = os.open(filename, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(f)
        with pytest.warns(None):
            yacmap.write(filename)
        os.remove(filename)


class TestExceptions:
    def test_cant_write_ro_mode(self, cfg_file, list_locks):
        yacmap = yacman.YacAttMap(filepath=cfg_file, writable=False)
        with pytest.raises(OSError):
            yacmap.write(cfg_file)

    def test_filename_required_when_object_created_from_mapping(self):
        yacmap = yacman.YacAttMap(entries={})
        with pytest.raises(TypeError):
            yacmap.write()

    def test_unlock_errors_when_no_filepath_provided(self, cfg_file):
        yacmap = yacman.YacAttMap({})
        with pytest.raises(TypeError):
            yacmap.unlock()

    def test_unlock_removes_lock_and_returns_true(self, cfg_file, list_locks):
        yacmap = yacman.YacAttMap(filepath=cfg_file, writable=True)
        assert yacmap.unlock()
        assert len(list_locks) == 0

    def test_unlock_returns_false_if_nothing_unlocked(self, cfg_file):
        yacmap = yacman.YacAttMap(filepath=cfg_file, writable=False)
        assert not yacmap.unlock()

    def test_warnings(self, cfg_file):
        with pytest.warns(None):
            yacman.YacAttMap({}, writable=True)
        with pytest.warns(DeprecationWarning):
            yacman.YacAttMap(entries=cfg_file)


class TestReading:
    def test_read_locked_file_in_ro_mode(self, data_path, cfg_file):
        yacmapin = yacman.YacAttMap(filepath=cfg_file, writable=True)
        yacmapin.newattr = "value"
        yacmapin.write()
        yacmapin2 = yacman.YacAttMap(filepath=cfg_file, writable=False)
        assert (yacmapin2.newattr == "value")

    def test_read_locked_file_in_rw_mode(self, data_path, cfg_file):
        """ Here we test that the object constructor waits for a second and raises a Runtime error """
        yacmap = yacman.YacAttMap(filepath=cfg_file, writable=True)
        with pytest.raises(RuntimeError):
            yacman.YacAttMap(filepath=cfg_file, writable=True, wait_max=1)
        yacmap.write()

    def test_locking_is_opt_in(self, cfg_file, locked_cfg_file):
        """
        this tests backwards compatibility, in the past the locking system did not exist.
        Consequently, to make yacman backwards compatible, multiple processes should be able to read and wrote to
        the file when no arguments but the intput are specified
        """
        yacman.YacAttMap(filepath=cfg_file)
        assert not os.path.exists(locked_cfg_file)


yaml_str = """\
---
one: 1
2: two
"""


def test_float_idx():
    data = yacman.YacAttMap(yamldata=yaml_str)
    # We should be able to access this by string, not by int index.
    assert(data['2'] == "two")
    with pytest.raises(KeyError):
        data[2]


def cleanup_locks(lcks):
    if lcks:
        [os.remove(l) for l in lcks]


def make_cfg_file_path(name, data_path):
    return os.path.join(data_path, name)


def make_lock_path(name, data_path):
    return os.path.join(data_path, yacman.LOCK_PREFIX + name)
