#!/usr/bin/python

# download_images_from_csv.py
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
Download images from CSV
============================================================

Download images from a CSV file

"""


import sys
import os.path
import argparse
import csv
import urllib2
import hashlib
from progressbar import ProgressBar, Percentage, Bar, \
        AdaptiveETA, AdaptiveTransferSpeed
from hurry.filesize import size, alternative
from common import set_verbose_level, print_verbose, dir_type, \
        VG_PREFIX, NVG_PREFIX, LABEL_SEPARATOR, VVG_ARTIST


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-c', '--csv', type=argparse.FileType('r'), required=True,
            help='csv file')
    parser.add_argument('-d', '--directory', type=dir_type, required=True,
            help='destination directory')
    parser.add_argument('-v', '--verbose', action='count', default=0,
            help='verbosity level')

    args = parser.parse_args(args=argv)
    return args

# Parse page entry
def parse_entry(dest_dir, page,
        idx_pageid, idx_imageurl, idx_sha1, idx_artist):

    # Get values
    pageid = page[idx_pageid]
    image_url = page[idx_imageurl]
    image_sha1 = page[idx_sha1]
    artist = page[idx_artist]

    if artist == VVG_ARTIST:
        prefx = VG_PREFIX
    else:
        prefx = NVG_PREFIX

    # Parse
    file_extension = os.path.splitext(image_url)[1]
    image_path = os.path.join(dest_dir,
            prefx + LABEL_SEPARATOR + pageid + file_extension)

    return image_path, image_url, image_sha1

# Download image
def download_image(img_path, img_url):

    # Fetch URL
    url = urllib2.urlopen(img_url)
    meta = url.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print_verbose("Downloading image %s (%s)" % (url.geturl(),
        size(file_size, system=alternative)), 0)

    # Set progress bar
    widgets = ['Progress: ', Percentage(), ' ', Bar(),
            ' ', AdaptiveETA(), ' ', AdaptiveTransferSpeed()]
    pbar = ProgressBar(widgets=widgets, maxval=file_size).start()

    # Download
    f = open(img_path, 'wb')
    file_size_dl = 0
    block_sz = 1024 * 8

    while True:
        buff = url.read(block_sz)
        if not buff:
            break

        file_size_dl += len(buff)
        f.write(buff)
        pbar.update(file_size_dl)

    # Done
    f.close()
    pbar.finish()
    return url.getcode()

# Check SHA1
def check_sha1(img_path, img_sha1):
    sha1 = hashlib.sha1()
    with open(img_path, 'rb') as f:
        sha1.update(f.read())

    if (img_sha1 != sha1.hexdigest()):
        raise ValueError("File '%s' SHA1 digest does not match" % img_path)
    return True

# Read CSV and download images
def download_from_csv(csvfile, dest_dir):

    # Define writer
    reader = csv.reader(csvfile, quoting=csv.QUOTE_ALL, strict=True)

    # Field names
    field_names = reader.next()

    # Indices
    idx_pageid = field_names.index('PageID')
    idx_imageurl = field_names.index('ImageURL')
    idx_sha1 = field_names.index('ImageSHA1')
    idx_artist = field_names.index('Artist')

    # For each page entry
    for page in reader:

        # Parse entry
        img_path, img_url, img_sha1 = parse_entry(dest_dir, page,
                idx_pageid, idx_imageurl, idx_sha1, idx_artist)

        # Download only if image does not exist
        if (not os.access(img_path, os.R_OK)):
            download_image(img_path, img_url)

        # Check SHA1
        check_sha1(img_path, img_sha1)


# Main
def main(argv):

    # Parse arguments
    args = parse_args(argv)
    set_verbose_level(args.verbose)

    print_verbose("Args: %s" % str(args), 1)

    # Download images
    download_from_csv(args.csv, args.directory)


if __name__ == "__main__":
    main(sys.argv[1:])

