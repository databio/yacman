import pytest
import yacman
import os
from warnings import warn

# for interactive testing, run from within code/yacman


def test_write(cfg_file, list_locks, data_path):
    yacmap = yacman.YacAttMap(filepath=cfg_file, ro=False, use_locks=True)
    yacmap.write(make_cfg_file_path("writeout.yaml", data_path))
    yacmapin = yacman.YacAttMap(filepath=make_cfg_file_path("writeout.yaml", data_path), ro=False, use_locks=True)
    yacmapin.newattr = "value"
    yacmapin.write()
    yacmapin2 = yacman.YacAttMap(filepath=make_cfg_file_path("writeout.yaml", data_path), use_locks=True, ro=True)
    assert (yacmapin2.newattr == "value")
    os.remove(make_cfg_file_path("writeout.yaml", data_path))

    conf = yacman.load_yaml(cfg_file)
    yacmap_nofile = yacman.YacAttMap(conf)
    with pytest.raises(Exception):
        yacmap_nofile.write()
    cleanup_locks(list_locks)


def test_entries_update(cfg_file, list_locks):
    conf = yacman.load_yaml(cfg_file)
    yacmap = yacman.YacAttMap(filepath=cfg_file, ro=True)
    yacmap = yacman.YacAttMap(filepath=cfg_file, ro=True)
    yacmap = yacman.YacAttMap(entries={"entry": "updated"}, ro=True)
    yacmap = yacman.YacAttMap(entries={"genome_folder": "updated"}, ro=True)
    assert(yacmap.genome_folder == "updated")
    yacmap = yacman.YacAttMap()
    cleanup_locks(list_locks)


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


@pytest.mark.parametrize("name", ["test.yaml", "test1.yaml"])
def test_warn_on_write_when_locked(name, list_locks, data_path):
    yacmap = yacman.YacAttMap(entries={"test": "data"})
    write_lock_flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    fd = os.open(make_cfg_file_path("lock." + name, data_path), write_lock_flags)
    os.close(fd)
    with pytest.warns(None):
        yacmap.write(make_cfg_file_path(name, data_path))
    os.remove(make_cfg_file_path(name, data_path))
    cleanup_locks(list_locks)


def test_cant_write_ro_mode(cfg_file, list_locks):
    yacmap = yacman.YacAttMap(filepath=cfg_file, use_locks=True, ro=True)
    with pytest.raises(OSError):
        yacmap.write(cfg_file)
    cleanup_locks(list_locks)


def test_lock_created_and_removed_after_successful_write(cfg_file, locked_cfg_file, list_locks):
    yacmap = yacman.YacAttMap(filepath=cfg_file, use_locks=True, ro=False)
    assert os.path.exists(locked_cfg_file)
    yacmap.write()
    assert not os.path.exists(locked_cfg_file)
    cleanup_locks(list_locks)


def test_filename_required_when_object_created_from_mapping():
    yacmap = yacman.YacAttMap(entries={})
    with pytest.raises(TypeError):
        yacmap.write()


def test_unlock(cfg_file, list_locks):
    yacmap = yacman.YacAttMap({})
    assert not yacmap.unlock()
    yacmap = yacman.YacAttMap(filepath=cfg_file, use_locks=True, ro=False)
    assert yacmap.unlock()
    assert len(list_locks) == 0


def test_make_ro(cfg_file, list_locks):
    yacmap = yacman.YacAttMap(filepath=cfg_file, ro=False)
    yacmap.make_ro()
    assert len(list_locks) == 0


def test_make_rw(cfg_file, list_locks, locked_cfg_file):
    yacmap = yacman.YacAttMap({}, ro=True)
    with pytest.raises(TypeError):
        yacmap.make_rw()
    yacmap.make_rw(cfg_file)
    assert os.path.exists(locked_cfg_file)
    cleanup_locks([locked_cfg_file])
