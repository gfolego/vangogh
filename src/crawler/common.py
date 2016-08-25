#!/usr/bin/python

# common.py
# Copyright 2016
#   Guilherme Folego (gfolego@gmail.com)
#   Otavio Gomes (otaviolmiro@gmail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



"""
============================================================
Common
============================================================

Common definitions

"""


import os
import argparse
from pprint import pprint
from functools import total_ordering


# Some constants
API_URL = 'https://commons.wikimedia.org/w/api.php'

DEFAULT_DENSITY = 196.3

VG_PREFIX = 'vg'
NVG_PREFIX = 'nvg'
LABEL_SEPARATOR = '_'
VVG_ARTIST = 'Vincent van Gogh'


# Some global values
verbose_lvl = 0


# Some functions
def dir_type(x):
    x = str(x)
    if not os.path.isdir(x):
        raise argparse.ArgumentTypeError("%s is not a valid directory" % x)
    if not os.access(x, os.R_OK):
        raise argparse.ArgumentTypeError("%s it nos a readable directory" % x)
    if not os.access(x, os.W_OK):
        raise argparse.ArgumentTypeError("%s it nos a writable directory" % x)
    return x


def get_verbose_level():
    global verbose_lvl
    return verbose_lvl


def set_verbose_level(lvl):
    global verbose_lvl
    if lvl is not None:
        verbose_lvl = lvl


def print_verbose(msg, lvl):
    if verbose_lvl >= lvl:
        print(msg)


def pprint_verbose(msg, lvl):
    if verbose_lvl >= lvl:
        pprint(msg)


@total_ordering
class ImagePage:
    def __init__(self, page_id, description_url, img_url, img_sha1,
            img_height, img_width, paint_id, artist, dim):
        self.page_id = int(page_id)
        self.description_url = description_url
        self.img_url = img_url
        self.img_sha1 = img_sha1
        self.img_height = int(img_height)
        self.img_width =  int(img_width)
        self.paint_id = paint_id
        self.artist = artist
        self.dim = dim

    def __lt__(self, other):
        return self.page_id < other.page_id

    def __eq__(self, other):
        return self.page_id == other.page_id

    def __str__(self):
        return '[%d %s %s %s %d %d %s %s %s]' % (self.page_id,
                self.description_url, self.img_url, self.img_sha1,
                self.img_height, self.img_width,
                self.paint_id, self.artist, self.dim)


