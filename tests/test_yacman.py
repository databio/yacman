import pytest
import yacman
import attmap
import os

def test_yaml_load():
	conf = yacman.load_yaml("conf.yaml")

	yacmap = yacman.YacAttMap("conf.yaml")
	yacmap2 = yacman.YacAttMap(conf)

	# Not sure why these are not equivalent:
	# assert(yacmap == yacmap2)

	# but they are at the map level:
	assert(yacmap.to_map() == yacmap2.to_map())

	yacmap

	# round trip
	test_yaml_filename = "pytest_test.yaml"
	yacmap.write(test_yaml_filename)
	obj = yacman.YacAttMap(test_yaml_filename)
	assert(yacmap.to_map() == obj.to_map())
	os.remove(test_yaml_filename)

	print(yacmap.to_yaml())
	assert(yacmap.genome_folder == os.path.expandvars("$GENOMES"))
	assert(yacmap2.genome_folder == os.path.expandvars("$GENOMES"))
	assert(yacmap.to_dict()["genome_folder"] == "$GENOMES")
	print(yacmap.genomes.to_yaml())


# import yacman
# conf = yacman.load_yaml("conf.yaml")
# conf
# attmap.OrdAttMap(conf)

