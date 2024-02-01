#!/usr/bin/env python3.11

import sys
import os

from argparse import ArgumentParser
from random import random
from time import sleep

from yacman import YacAttMap
from yacman import FutureYAMLConfigManager as YAMLConfigManager
from yacman import write_lock

import logging
_LOGGER = logging.getLogger()  # root logger
stream = logging.StreamHandler(sys.stdout)
fmt = logging.Formatter("%(levelname)s %(asctime)s | %(name)s:%(module)s:%(lineno)d > %(message)s ")
stream.setFormatter(fmt)
_LOGGER.setLevel(os.environ.get("LOGLEVEL", "DEBUG"))
_LOGGER.addHandler(stream)


parser = ArgumentParser(description="Test script")

parser.add_argument("-p", "--path", help="path to the test file", required=True)
parser.add_argument("-i", "--id", help="process id", required=True)
parser.add_argument("-w", "--wait", help="max wait time", type=int, required=True)
args = parser.parse_args()
ym = YAMLConfigManager.from_yaml_file(args.path, wait_max=args.wait)

with write_lock(ym) as locked_y:
    locked_y.rebase()
    random_wait_time = random()
    _LOGGER.debug(f"Sleeping for {random_wait_time} to simulate process {args.id} updating the file")
    sleep(random_wait_time)
    locked_y.update({args.id: 1})
    _LOGGER.debug(f"Writing to file for process {args.id}.")
    locked_y.write()


raise SystemExit
# sys.exit(0)
