import pytest
import yacman
import os
from glob import glob

# for interactive testing, run from within code/yacman


def test_yaml_load():
    conf = yacman.load_yaml("conf.yaml")
    yacmap = yacman.YacAttMap("conf.yaml", ro=False)
    yacmap2 = yacman.YacAttMap(conf)

    # Not sure why these are not equivalent:
    # assert(yacmap == yacmap2)

    # but they are at the yaml level:
    assert(yacmap.to_yaml() == yacmap2.to_yaml())
    yacmap

    # round trip
    test_yaml_filename = "pytest_test.yaml"
    yacmap.write(test_yaml_filename)
    obj = yacman.YacAttMap(test_yaml_filename)
    assert(yacmap.to_yaml() == obj.to_yaml())
    os.remove(test_yaml_filename)
    print(yacmap.to_yaml())
    assert(yacmap.genome_folder == os.path.expandvars("$GENOMES"))
    assert(yacmap2.genome_folder == os.path.expandvars("$GENOMES"))
    assert(yacmap.to_dict()["genome_folder"] == "$GENOMES")
    print(yacmap.genomes.to_yaml())
    yacmap._file_path
    cleanup_locks()


def test_write():
    yacmap = yacman.YacAttMap("conf.yaml", ro=False)
    yacmap.write("writeout.yaml")

    yacmapin = yacman.YacAttMap("writeout.yaml", ro=False)
    yacmapin.newattr = "value"
    yacmapin.write()
    yacmapin2 = yacman.YacAttMap("writeout.yaml")
    assert (yacmapin2.newattr == "value")
    os.remove("writeout.yaml")

    conf = yacman.load_yaml("conf.yaml")
    yacmap_nofile = yacman.YacAttMap(conf)
    with pytest.raises(Exception):
        yacmap_nofile.write()
    cleanup_locks()


def test_entries_update():
    conf = yacman.load_yaml("conf.yaml")
    yacmap = yacman.YacAttMap("conf.yaml", ro=True)
    yacmap = yacman.YacAttMap(filepath="conf.yaml", ro=True)
    yacmap = yacman.YacAttMap({"entry": "updated"}, filepath="conf.yaml", ro=True)
    yacmap = yacman.YacAttMap({"genome_folder": "updated"}, filepath="conf.yaml", ro=True)
    assert(yacmap.genome_folder == "updated")
    yacmap = yacman.YacAttMap()
    cleanup_locks()


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


def get_locks():
    return glob("lock.*")


def cleanup_locks():
    lcks = get_locks()
    if lcks:
        [os.remove(l) for l in lcks]


@pytest.mark.parametrize("name", ["test.yaml", "test1.yaml"])
def test_cant_write_when_locked(name):
    yacmap = yacman.YacAttMap({"test": "data"})
    write_lock_flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    fd = os.open("lock." + name, write_lock_flags)
    os.close(fd)
    with pytest.raises(OSError):
        yacmap.write(name)
    cleanup_locks()


def test_cant_write_ro_mode(name="conf.yaml"):
    yacmap = yacman.YacAttMap(name, ro=True)
    with pytest.raises(OSError):
        yacmap.write(name)
    cleanup_locks()


def test_lock_created_and_removed_after_successful_write(name="conf.yaml"):
    yacmap = yacman.YacAttMap(name, ro=False)
    assert len(get_locks()) != 0
    assert os.path.exists("lock." + name)
    yacmap.write()
    assert not os.path.exists("lock." + name)
    cleanup_locks()


