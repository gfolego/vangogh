#!/usr/bin/python

# caffe_extract_features.py
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
Extract Features (Caffe)
============================================================

Extract features from images using a Caffe model.

Currently, the mean pixel value from VGG is used,
which is [103.939, 116.779, 123.68]  (BGR).

References:
  http://caffe.berkeleyvision.org/
  http://www.robots.ox.ac.uk/~vgg/research/very_deep/

"""


import sys
import os
import argparse
import numpy as np
import caffe
from common import dir_type, file_type, VGG_MEAN_PIXEL, \
    print_verbose, set_verbose_level, get_verbose_level, \
    CAFFE_BATCH_SIZE


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-p', '--proto', type=file_type, required=True,
                        help='prototxt file of the net model')
    parser.add_argument('-m', '--model', type=file_type, required=True,
                        help='caffemodel file of the net model')
    parser.add_argument('-l', '--list', type=file_type, required=True,
                        help='file containing list of images to process')
    parser.add_argument('-i', '--input', type=dir_type, required=True,
                        help='input images directory')
    parser.add_argument('-o', '--output', type=dir_type, required=True,
                        help='output features directory')
    parser.add_argument('-v', '--verbose', action='count',
                        help='verbosity level')

    args = parser.parse_args(args=argv)
    return args



# Main
def main(argv):

    # Parse arguments
    args = parse_args(argv)
    set_verbose_level(args.verbose)

    print_verbose("Args: %s" % str(args), 1)

    # Adapted from
    # https://nbviewer.jupyter.org/github/BVLC/caffe/blob/master/examples/00-classification.ipynb
    np.set_printoptions(threshold=np.nan)

    caffe.set_mode_cpu()
    net = caffe.Net(args.proto, args.model, caffe.TEST)

    # input preprocessing: 'data' is the name of the input blob == net.inputs[0]
    transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
    transformer.set_transpose('data', (2,0,1))
    transformer.set_mean('data', VGG_MEAN_PIXEL) # mean pixel
    transformer.set_raw_scale('data', 255)  # the reference model operates on images in [0,255] range instead of [0,1]
    transformer.set_channel_swap('data', (2,1,0))  # the reference model has channels in BGR order instead of RGB

    # Read image names
    with open(args.list) as f:
        allnames = f.read().splitlines()

    for sub in xrange(0, len(allnames), CAFFE_BATCH_SIZE):
        fnames = allnames[sub : sub+CAFFE_BATCH_SIZE]

        # Reshape input data
        print net.blobs['data'].data.shape
        net.blobs['data'].reshape(len(fnames), *net.blobs['data'].shape[1:])
        print net.blobs['data'].data.shape

        # Preprocess images
        for idx, fname in enumerate(fnames):
            fpath = os.path.join(args.input, fname)
            print "Processing image %s ..." % fpath
            img = transformer.preprocess('data', caffe.io.load_image(fpath))
            net.blobs['data'].data[idx] = img

        # Extract features
        print "Extracting features ..."
        out = net.forward()

        # Write extracted features
        for idx, fname in enumerate(fnames):
            path = os.path.join(args.output, os.path.dirname(fname))
            if not os.path.exists(path):
                os.makedirs(path)
            fpath = os.path.join(args.output, fname + ".feat")
            print "Writing features to %s ..." % fpath
            np.savetxt(fpath, net.blobs['fc7'].data[idx])

    print "Done!"


if __name__ == "__main__":
    main(sys.argv[1:])

