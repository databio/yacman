import pytest

import yacman

def test_yaml_load():
	conf = yacman.load_yaml("conf.yaml")

	yacmap = yacman.YacAttMap("conf.yaml")
	yacmap = yacman.YacAttMap(conf)



import yacman
import attmap
conf = yacman.load_yaml("conf.yaml")
conf
attmap.OrdAttMap(conf)

