#!/usr/bin/python

# crawler.py
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
Crawler
============================================================

Crawl a given URL

"""


import sys
import argparse
from os.path import basename
from urllib import unquote_plus
from wikitools import wiki, api
from common import set_verbose_level, print_verbose, pprint_verbose, API_URL


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-u', '--url', type=str, required=True,
            help='page url')
    parser.add_argument('-v', '--verbose', action='count',
            help='verbosity level')

    args = parser.parse_args(args=argv)
    return args


def crawl(url_param):

    # Fix eventual full URL
    url_param = unquote_plus(basename(url_param))

    # Generate query
    params = {
            'action'        : 'query',
            'prop'          : 'imageinfo|revisions',
            'iiprop'        : 'url|sha1|size',
            'rvprop'        : 'content',
            'rawcontinue'   : '' }

    url_type = get_url_type(url_param)

    if url_type == 'category':
        params['generator'] = 'categorymembers'
        params['gcmtitle']  = url_param
        params['gcmlimit']  = 'max'
    elif url_type == 'file':
        params['titles']    = url_param
    else:
        params['generator'] = 'images'
        params['titles']    = url_param
        params['gimlimit']  = 'max'


    # Call API
    site = wiki.Wiki(API_URL)
    request = api.APIRequest(site, params)

    print_verbose("Site: %s" % str(site), 2)
    print_verbose("Query: ", 2)
    pprint_verbose(params, 2)

    result = request.query(querycontinue=True)
    print_verbose("Result: ", 4)
    pprint_verbose(result, 4)

    # Check result
    if 'error' in result:
        raise Error(result['error'])

    if 'warnings' in result:
        sys.stderr.write(result['warnings'])
        return None

    if '-1' in result['query']['pages']:
        sys.stderr.write(result['query']['pages']['-1'])
        return None

    return result['query']['pages']



# Get URL type
def get_url_type(url_param):
    if url_param.startswith('Category:'):
        return 'category'
    elif url_param.startswith('File:'):
        return 'file'
    return 'default'


# Main
def main(argv):

    # Parse arguments
    args = parse_args(argv)
    set_verbose_level(args.verbose)

    print_verbose("Args: %s" % str(args), 1)

    # Crawl URL
    crawl(args.url)


if __name__ == "__main__":
    main(sys.argv[1:])

