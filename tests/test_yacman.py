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


# import yacman
# conf = yacman.load_yaml("conf.yaml")
# conf
# attmap.OrdAttMap(conf)


# y = load_yaml("/home/nsheff/Dropbox/env/bulker_config/puma.yaml")

# f = "/home/nsheff/Dropbox/env/bulker_config/puma.yaml"
# import yacman
# y2 = yacman.YacAttMap(f)
# y2["bulker"]["crates"]["databio"]["lab"]["1.0"]




# yaml_str = """\
# ---
# one: 1
# 2: two
# """
# import yaml
# import inspect
# inspect.getsourcelines(yaml.SafeLoader.construct_mapping)
# yaml.safe_load(yaml_str)


# def my_construct_mapping(self, node, deep=False):
#     data = self.construct_mapping_org(node, deep)
#     return {(str(key) if isinstance(key, float) or isinstance(key, int) else key): data[key] for key in data}

# def construct_pairs(self, node, deep=False):
#     # if not isinstance(node, MappingNode):
#     #     raise ConstructorError(None, None,
#     #             "expected a mapping node, but found %s" % node.id,
#     #             node.start_mark)
#     pairs = []
#     for key_node, value_node in node.value:
#         key = str(self.construct_object(key_node, deep=deep))
#         value = self.construct_object(value_node, deep=deep)
#         pairs.append((key, value))
#     return pairs

# yaml.SafeLoader.construct_mapping_org = yaml.SafeLoader.construct_mapping
# yaml.SafeLoader.construct_mapping = my_construct_mapping
# yaml.SafeLoader.construct_pairs = construct_pairs



# yaml.safe_load(yaml_str)


# import oyaml
# inspect.getsourcelines(oyaml.SafeLoader.construct_mapping)


# def map_constructor2(loader, node):
#     loader.flatten_mapping(node)
#     pairs = loader.construct_pairs(node)

#     try:
#         return OrderedDict(pairs)
#     except TypeError:
#         loader.construct_mapping(node)  # trigger any contextual error
#         raise

# pyyaml.add_constructor("tag:yaml.org,2002:map", map_constructor, Loader=yaml.SafeLoader)

# oyaml.safe_load(yaml_str)
# yaml.safe_load(yaml_str)




# yaml.safe_load(yaml_str)


# import ruamel.yaml
# from ruamel.yaml import YAML
# yaml = YAML()

# yaml.load(yaml_str)

