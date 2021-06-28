#!/usr/bin/env python3

import sys
from argparse import ArgumentParser
from random import random
from time import sleep

from yacman import YacAttMap

parser = ArgumentParser(description="Test script")

parser.add_argument("-p", "--path", help="path to the test file", required=True)
parser.add_argument("-i", "--id", help="process id", required=True)
parser.add_argument("-w", "--wait", help="max wait time", type=int, required=True)
args = parser.parse_args()
yam = YacAttMap(filepath=args.path, wait_max=args.wait)
with yam as y:
    sleep(random())
    y.update({args.id: 1})

sys.exit(0)
