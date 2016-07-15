#!/usr/bin/python

"""
============================================================
Gather data
============================================================

Gather data from folder and generate
data matrix, labels and classes

"""


import sys
import os
import argparse
from multiprocessing import cpu_count, Pool
import numpy as np

from common import VG_CLASS, VG_PREFIX, NVG_CLASS, NVG_PREFIX, LABEL_SEPARATOR,\
    dir_type, print_verbose, set_verbose_level, get_n_cores, set_n_cores


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-d', '--dir', type=dir_type, required=True,
                        help='data directory')
    parser.add_argument('-c', '--cores', default=get_n_cores(), type=int,
                        choices=xrange(1, cpu_count()+1),
                        help='number of cores to be used (default: %d)' % get_n_cores())
    parser.add_argument('-v', '--verbose', action='count',
                        help='verbosity level')

    args = parser.parse_args(args=argv)
    return args


def apply_multicore_function(fn, arg_list):
    print_verbose('Processing function %s with: %s' % (str(fn), str(arg_list)), 5)
    pool = Pool(processes=get_n_cores())
    ret = pool.map(fn, arg_list)
    return ret


def list_files(dirname):
    files = sorted([fn for fn in os.listdir(dirname)
                if os.path.isfile(os.path.join(dirname, fn))])
    print_verbose('Dir %s files: %s' % (dirname, str(files)), 3)
    return files


def read_data(filename):
    print_verbose('Reading data from file %s ...' % filename, 3)
    data = np.loadtxt(filename)
    print_verbose('File %s features count: %s' % (filename, data.shape), 4)
    print_verbose('Data read: %s' % str(data), 5)
    return data


def parse_class(filename):
    if filename.startswith(VG_PREFIX):
        cl = VG_CLASS
    elif filename.startswith(NVG_PREFIX):
        cl = NVG_CLASS
    else:
        raise ValueError('Invalid class prefix.'
                         'Valid prefixes are "%s" and "%s"' % (VG_PREFIX, NVG_PREFIX))

    print_verbose('File %s class: %d' % (filename, cl), 4)
    return cl


def parse_label(filename):
    groups = filename.split(LABEL_SEPARATOR)
    label = LABEL_SEPARATOR.join(groups[:2])
    print_verbose('File %s label: %s' % (filename, label), 4)
    return label


def gen_data(dirname):
    files = list_files(dirname)
    full_paths = map(lambda x: os.path.join(dirname, x), files)
    print_verbose('Dir %s full file path: %s' % (dirname, str(full_paths)), 4)

    data = apply_multicore_function(read_data, full_paths)
    labels = apply_multicore_function(parse_label, files)
    classes = apply_multicore_function(parse_class, files)

    data = np.asarray(data, dtype=np.float)
    labels = np.asarray(labels, dtype=np.str)
    classes = np.asarray(classes, dtype=np.uint8)

    return data, labels, classes


def main(argv):

    # Parse arguments
    args = parse_args(argv)
    set_verbose_level(args.verbose)
    set_n_cores(args.cores)

    print_verbose("Args: %s" % str(args), 1)

    data, labels, classes = gen_data(args.dir)

    print_verbose('Data: %s' % str(data), 5)
    print_verbose('Labels: %s' % str(labels), 4)
    print_verbose('Classes: %s' % str(classes), 4)

    print_verbose('Data shape: %s' % str(data.shape), 2)
    print_verbose('Labels shape: %s' % str(labels.shape), 2)
    print_verbose('Classes shape: %s' % str(classes.shape), 2)


if __name__ == "__main__":
    main(sys.argv[1:])
