# -*- coding: utf-8 -*-
# OpenCS Git Work History - A simple Git Report Generator
# Copyright(C) 2021 Open Communications Security
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY
# without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see < https: // www.gnu.org/licenses/>.
import unittest
import json
from pathlib import Path
#from .parser import *

ROOT_DIR = Path(__file__).parent.parent
SAMPLE_DIR = ROOT_DIR / 'unittest-samples'
TEST_CONFIG_FILE = ROOT_DIR / 'test-config.json'
if TEST_CONFIG_FILE.exists():
    with open(TEST_CONFIG_FILE, 'r') as inp:
        TEST_CONFIG = json.load(inp)
else:
    TEST_CONFIG = None
