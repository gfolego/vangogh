#!/usr/bin/python

# patch_extraction.py
# Copyright (C) 2016
#   Guilherme Folego (gfolego@gmail.com)
#   Otavio Gomes (otaviolmiro@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.



"""
============================================================
Patch extraction
============================================================

Extract patches from an image

"""


import sys
import os
import argparse
from multiprocessing import cpu_count
from skimage.util import view_as_windows
from matplotlib.pyplot import imread, imsave

from common import WINDOW_SIZE, dir_type, file_type, print_verbose, set_verbose_level, get_n_cores, set_n_cores


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-i', '--image', type=file_type, required=True,
                        help='input image')
    parser.add_argument('-d', '--dir', type=dir_type, required=True,
                        help='destination directory')
    parser.add_argument('-w', '--window', default=WINDOW_SIZE, type=int,
                        help='window size [NxN] (default: %d)' % WINDOW_SIZE)
    parser.add_argument('-s', '--step', default=WINDOW_SIZE, type=int,
                        help='step size (default: %d)' % WINDOW_SIZE)
    parser.add_argument('-c', '--cores', default=get_n_cores(), type=int,
                        choices=xrange(1, cpu_count()+1),
                        help='number of cores to be used (default: %d) -- currently not used' % get_n_cores())
    parser.add_argument('-v', '--verbose', action='count',
                        help='verbosity level')

    args = parser.parse_args(args=argv)
    return args


def save_img(im, path):
    print_verbose("Saving patch %s ..." % path, 3)
    imsave(path, im)


def gen_patch_path(im_path, dest_dir, id):
    # Determine new filename
    filename = os.path.basename(im_path)
    filename, ext = os.path.splitext(filename)
    newname = "%s_%04d%s" % (filename, id, ext)

    # Determine full path
    dest_path = os.path.join(dest_dir, newname)

    return dest_path


def patch_extract(im_path, window_size, step_size, dest_dir):

    # Read image
    im = imread(im_path)
    print_verbose("Original image shape: %s" % str(im.shape), 5)

    # Adjust borders
    pos_x = int(((im.shape[0] - window_size) % step_size)/2)
    pos_y = int(((im.shape[1] - window_size) % step_size)/2)
    print_verbose("Position: %s" % str((pos_x, pos_y)), 5)
    im = im[pos_x:, pos_y:, :]
    print_verbose("New image shape: %s" % str(im.shape), 5)

    # Generate window shape
    window_shape = (window_size, window_size, im.shape[2])
    print_verbose("Window shape: %s" % str(window_shape), 5)

    # Generate view
    view = view_as_windows(im, window_shape, step_size)
    print_verbose("View shape: %s" % str(view.shape), 5)

    id = 0
    for i in range(view.shape[0]):
        for j in range(view.shape[1]):

            # Generate patch path
            dest_path = gen_patch_path(im_path, dest_dir, id)
            print_verbose("Patch path: %s" % str(dest_path), 5)

            # Extract view
            tmp_view = view[i, j, 0, :, :, :]
            print_verbose("Current view shape: %s" % str(tmp_view.shape), 5)

            # Save patch
            save_img(tmp_view, dest_path)
            id += 1


def main(argv):

    # Parse arguments
    args = parse_args(argv)
    set_verbose_level(args.verbose)
    set_n_cores(args.cores)

    print_verbose("Args: %s" % str(args), 1)

    # Extract patches
    patch_extract(args.image, args.window, args.step, args.dir)


if __name__ == "__main__":
    main(sys.argv[1:])
