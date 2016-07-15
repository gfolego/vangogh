#!/usr/bin/python

"""
============================================================
Resize images
============================================================

Resize images to standard density

"""


import sys
import os.path
import argparse
import csv
from math import ceil
from subprocess import check_call, check_output, list2cmdline
from multiprocessing import Pool
from common import set_verbose_level, get_verbose_level, print_verbose, \
    dir_type, DEFAULT_DENSITY


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-c', '--csv', type=argparse.FileType('r'), required=True,
            help='csv file')
    parser.add_argument('-o', '--original', type=dir_type, required=True,
            help='directory containing original images')
    parser.add_argument('-r', '--resized', type=dir_type, required=True,
            help='directory for resized images')
    parser.add_argument('-d', '--density', type=float, default=DEFAULT_DENSITY,
            help='standard density (default: %.2f)' % DEFAULT_DENSITY)
    parser.add_argument('-v', '--verbose', action='count',
            help='verbosity level')

    args = parser.parse_args(args=argv)
    return args

# Parse paths from page entry
def parse_entry_paths(orig_dir, dest_dir, pageid, img_url):
    file_extension = os.path.splitext(img_url)[1]
    orig_path = os.path.join(orig_dir, pageid + file_extension)
    dest_path = os.path.join(dest_dir, pageid + '.png')
    return orig_path, dest_path

# Parse final dimensions in pixels from real dimensions in inches
def parse_entry_sizes(density, realheight, realwidth):
    pixelheight = int(ceil(density * realheight))
    pixelwidth = int(ceil(density * realwidth))
    return pixelheight, pixelwidth

# Call convert (ImageMagick) to resize image
def convert_resize(orig_path, dest_path, pixelheight, pixelwidth):
    # Prepare command
    cmd = ["convert", orig_path, "-resize",
                  "%dx%d^" % (pixelwidth, pixelheight), dest_path]
    if get_verbose_level() >= 5:
        cmd.insert(1, "-verbose")

    # Run
    print_verbose("Running command: " + list2cmdline(cmd), 3)
    return check_call(cmd)

# Call identify (ImageMagick) to get final dimensions in pixels
def identify_size(filepath):
    # Prepare command
    cmd = ["identify", "-format", "%h %w", filepath]
    if get_verbose_level() >= 6:
        cmd.insert(1, "-verbose")

    # Run
    dims = str(check_output(cmd)).split()
    h = int(dims[0])
    w = int(dims[1])
    return h, w

# Call convert (ImageMagick) to set density metadata
def convert_density(filepath, realheight, realwidth):
    # Get image dimensions in pixels
    pixelheight, pixelwidth = identify_size(filepath)

    # Calculate densities
    # Densities are calculated in CM due to precision errors in ImageMagick
    dens_height = 1.0 * pixelheight / realheight / 2.54
    dens_width = 1.0 * pixelwidth / realwidth / 2.54

    # Prepare command
    cmd = ["convert", "-units", "PixelsPerCentimeter", filepath,
                    "-density", "%.5fx%.5f" % (dens_width, dens_height),
                    filepath]
    if get_verbose_level() >= 5:
        cmd.insert(1, "-verbose")

    # Run
    print_verbose("Running command: " + list2cmdline(cmd), 3)
    return check_call(cmd)


# Perform the resize operation
def resize_image(page):

    # Global params
    global gb_idx_pageid
    global gb_idx_img_url
    global gb_idx_realheight
    global gb_idx_realwidth
    global gb_density
    global gb_orig_dir
    global gb_dest_dir

    # Parse values
    pageid = page[gb_idx_pageid]
    img_url = page[gb_idx_img_url]
    realheight = float(page[gb_idx_realheight])
    realwidth = float(page[gb_idx_realwidth])

    # Parse paths
    orig_path, dest_path = parse_entry_paths(gb_orig_dir, gb_dest_dir, pageid, img_url)

    # Parse dimensions
    pixelheight, pixelwidth = parse_entry_sizes(gb_density, realheight, realwidth)

    # Call convert to resize image
    convert_resize(orig_path, dest_path, pixelheight, pixelwidth)

    # Call convert to update density metadata
    convert_density(dest_path, realheight, realwidth)

    print_verbose('Done processing pageid %s' % pageid, 0)


# Read CSV and resize images
def resize_from_csv(csvfile, orig_dir, dest_dir, density):

    # Global params
    global gb_idx_pageid
    global gb_idx_img_url
    global gb_idx_realheight
    global gb_idx_realwidth
    global gb_density
    global gb_orig_dir
    global gb_dest_dir

    # Define writer
    reader = csv.reader(csvfile, quoting=csv.QUOTE_ALL, strict=True)

    # Field names
    field_names = reader.next()

    # Indices
    gb_idx_pageid = field_names.index('PageID')
    gb_idx_img_url = field_names.index('ImageURL')
    gb_idx_realheight = field_names.index('RealHeightInches')
    gb_idx_realwidth = field_names.index('RealWidthInches')

    # Prepare multicore execution
    gb_orig_dir = orig_dir
    gb_dest_dir = dest_dir
    gb_density = density

    pool = Pool()
    pool.map(resize_image, reader)
    pool.close()
    pool.join()

    print_verbose('Completed!', 0)



# Main
def main(argv):

    # Parse arguments
    args = parse_args(argv)
    set_verbose_level(args.verbose)

    print_verbose("Args: %s" % str(args), 1)

    # Resize images
    resize_from_csv(args.csv, args.original, args.resized, args.density)


if __name__ == "__main__":
    main(sys.argv[1:])

