import pytest
import attmap


def test_yaml_load():
	conf = yacman.load_yaml("conf.yaml")

	yacmap = yacman.YacAttMap("conf.yaml")
	yacmap2 = yacman.YacAttMap(conf)

	assert(yacmap == yacmap2)

	yacmap
	assert(yacmap.genome_folder == "$GENOMES")
	assert(yacmap2.genome_folder == "$GENOMES")
	print(yacmap.genomes.to_yaml())

	# test order





import yacman
conf = yacman.load_yaml("conf.yaml")
conf
attmap.OrdAttMap(conf)

