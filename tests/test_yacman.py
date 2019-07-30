import pytest
import yacman
import os

# for interactive testing, run from within code/yacman

def test_yaml_load():
    conf = yacman.load_yaml("conf.yaml")
    yacmap = yacman.YacAttMap("conf.yaml")
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


def test_entries_update():
    conf = yacman.load_yaml("conf.yaml")
    yacmap = yacman.YacAttMap("conf.yaml")
    yacmap = yacman.YacAttMap(filepath="conf.yaml")
    yacmap = yacman.YacAttMap({"entry": "updated"}, filepath="conf.yaml")
    yacmap = yacman.YacAttMap({"genome_folder": "updated"}, filepath="conf.yaml")
    assert(yacmap.genome_folder == "updated")
    yacmap = yacman.YacAttMap()



def test_write():
    yacmap = yacman.YacAttMap("conf.yaml")
    yacmap.write("writeout.yaml")

    yacmapin = yacman.YacAttMap("writeout.yaml")
    yacmapin.newattr = "value"
    yacmapin.write()
    yacmapin2 = yacman.YacAttMap("writeout.yaml")
    assert (yacmapin2.newattr == "value")
    os.remove("writeout.yaml")

    conf = yacman.load_yaml("conf.yaml")
    yacmap_nofile = yacman.YacAttMap(conf)
    with pytest.raises(Exception):
        yacmap_nofile.write()



# import yacman
# conf = yacman.load_yaml("conf.yaml")
# conf
# attmap.OrdAttMap(conf)

