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
import numpy as np


# Some constants
VGG_MEAN_PIXEL = np.array([103.939, 116.779, 123.68])

VG_CLASS = 1
NVG_CLASS = 0

VG_PREFIX = 'vg'
NVG_PREFIX = 'nvg'
LABEL_SEPARATOR = '_'

C_RANGE = 2.0 ** np.arange(-10, 16)
GAMMA_RANGE = 2.0 ** np.arange(-15, 4)
CLASS_WEIGHTS = [None, 'balanced']

K_FOLD = 3

CACHE_SIZE = 1000
N_ITER = 10

WINDOW_SIZE = 224

CAFFE_BATCH_SIZE = 10


# Score model
SCORE_MAX_ITER = 1000
SCORE_K_FOLD = 5


# Some global values
verbose_lvl = 0
n_cores = 1


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


def file_type(x):
    x = str(x)
    if not os.path.isfile(x):
        raise argparse.ArgumentTypeError("%s is not a valid file" % x)
    if not os.access(x, os.R_OK):
        raise argparse.ArgumentTypeError("%s it nos a readable file" % x)
    return x


def iter_type(x):
    x = int(x)
    if x <= 0:
        raise argparse.ArgumentTypeError("Minimum number of iterations is 1")
    return x


def get_verbose_level():
    global verbose_lvl
    return verbose_lvl


def set_verbose_level(lvl):
    global verbose_lvl
    verbose_lvl = lvl


def print_verbose(msg, lvl):
    if verbose_lvl >= lvl:
        print(msg)


def get_n_cores():
    global n_cores
    return n_cores


def set_n_cores(n):
    global n_cores
    n_cores = n
