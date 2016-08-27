#!/usr/bin/python

# crawl2csv.py
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
Crawl to CSV
============================================================

Crawl a given URL and extract raw data to CSV

"""


import sys
import argparse
import csv
from re import search
from crawler import crawl
from common import set_verbose_level, print_verbose, ImagePage


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-u', '--url', type=str, required=True,
            help='page url')
    parser.add_argument('-c', '--csv', type=argparse.FileType('w'), required=True,
            help='csv file')
    parser.add_argument('-v', '--verbose', action='count', default=0,
            help='verbosity level')

    args = parser.parse_args(args=argv)
    return args


# Extract some raw data from image content
def extract_image_content(content):

    # Avoid errors
    content = content.encode('ascii', errors='backslashreplace')

    # Paint ID
    m = search(r"(?i)(?:^|\|)\s?(?:id|references|accession number|notes)\s*=\s*\[*{*(?P<id>[{\w].*?)}*\]*(?:\n(?:\s*\||\*)|$)",
            content)
    paint_id = m.group('id') if m is not None else None

    # Artist
    m = search(r"(?i)(?:^|\|)\s?(?:commons_)?(?:artist|author)\s*=\s*{*(?:creator:)?(?P<artist>.*?)}*\s*(?:\n\s*\||$)",
            content)
    artist = m.group('artist') if m is not None else None

    # Dimensions
    m = search(r"(?i)(?:^|\|)\s?(?:pretty_)?dimensions\s*=\s*{*(?P<dim>.*?)}*(?:\n\s*\||$)",
            content)
    dim = m.group('dim') if m is not None else None

    return (paint_id, artist, dim)


# Extract raw data
def extract_data(result):

    img_list = []

    # For each page
    for page in result.values():

        # Get ID
        page_id = page['pageid']
        print_verbose("Extracting info from %s ..." % page_id, 1)

        try:
            # Image info
            img_info = page['imageinfo'][0]
            img_desc_url = img_info['descriptionurl']
            img_url = img_info['url']
            img_sha1 = img_info['sha1']
            img_height = img_info['height']
            img_width = img_info['width']

            # Content
            img_content = page['revisions'][0]['*']
            (paint_id, artist, dim) = extract_image_content(img_content)

            print_verbose("URL is %s" % img_desc_url, 1)

            # Internal object
            img_page = ImagePage(page_id, img_desc_url, img_url, img_sha1,
                    img_height, img_width,
                    paint_id, artist, dim)

            print_verbose(img_page, 3)
            img_list.append(img_page)
        except Exception as e:
            sys.stderr.write("Error processing PageID %s\n" % page_id)
            sys.stderr.write("-- %s\n" % e)


    return img_list


# Save raw image data to CSV file
def gen_csv(csvfile, page_list):

    # Define writer
    writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)

    # Field names
    field_names = ['PageID', 'DescriptionURL', 'ImageURL', 'ImageSHA1',
            'PixelHeight', 'PixelWidth',
            'PaintingID', 'Artist', 'RealDimensions']

    writer.writerow(field_names)

    # For each image
    for page in page_list:
        writer.writerow([page.page_id, page.description_url, page.img_url,
            page.img_sha1, page.img_height, page.img_width,
            page.paint_id, page.artist, page.dim])


# Main
def main(argv):

    # Parse arguments
    args = parse_args(argv)
    set_verbose_level(args.verbose)

    print_verbose("Args: %s" % str(args), 1)

    # Crawl URL
    result = crawl(args.url)

    # Extract data
    raw_data = extract_data(result)

    # Sort (optional)
    raw_data.sort()

    # Save to CSV
    gen_csv(args.csv, raw_data)



if __name__ == "__main__":
    main(sys.argv[1:])

