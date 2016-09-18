#!/usr/bin/python

# get_scores.py
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
Get scores
============================================================

Calculate score probabilities

"""


import sys
import argparse
from multiprocessing import cpu_count
import numpy as np
import cPickle as pickle

from common import dir_type, file_type, print_verbose, set_verbose_level, get_verbose_level, get_n_cores, set_n_cores

from gather_data import gen_data


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-d', '--dir', type=dir_type, required=True,
                        help='data directory')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='verbosity level')
    parser.add_argument('-c', '--cores', default=get_n_cores(), type=int,
                        choices=xrange(1, cpu_count()+1),
                        help='number of cores to be used (default: %d)' % get_n_cores())
    parser.add_argument('-m', '--model', type=str, required=True,
                        help='path to import the classifier model')
    parser.add_argument('-s', '--score', type=str, required=True,
                        help='path to import the score model')
    parser.add_argument('-t', '--targets', type=file_type, required=True,
                        help='input file with target labels')
    parser.add_argument('-n', '--number', type=int, default=2,
                        help='number of patches to analyze')


    args = parser.parse_args(args=argv)
    return args


def calc_prob(data, labels, args):

    classification = {}

    # Read models
    with open(args.model, "rb") as f:
        clf_model = pickle.load(f)
    print_verbose("Classifier Model [%0.2f%%]: %s" % (clf_model.best_score_*100, str(clf_model.best_estimator_)), 4)

    with open(args.score, "rb") as f:
        score_model = pickle.load(f)
    print_verbose("Score Model [%0.2f%%]: %s" % (score_model.best_score_*100, str(score_model.best_estimator_)), 4)

    # Read targets
    with open(args.targets) as f:
        targets = f.read().splitlines()

    # Get results
    for t in targets:

        print_verbose("Calculating label %s ..." % t, 0)

        idx = labels == t
        dist = clf_model.decision_function(data[idx])
        dist = np.sort(dist).reshape(-1, 1)

        # First
        prob = score_model.predict_proba(dist[:args.number])
        print_verbose("First scores:\n%s" % str(prob), 0)

        # Last
        prob = score_model.predict_proba(dist[-args.number:])
        print_verbose("Last scores:\n%s" % str(prob), 0)

    return 0


def main(argv):

    # Parse arguments
    args = parse_args(argv)
    set_verbose_level(args.verbose)
    set_n_cores(args.cores)

    print_verbose("Args: %s" % str(args), 1)

    # Some tests
    data, labels = gen_data(args.dir, False)

    print_verbose('Data: %s' % str(data), 5)
    print_verbose('Labels: %s' % str(labels), 4)

    print_verbose('Data shape: %s' % str(data.shape), 2)
    print_verbose('Labels shape: %s' % str(labels.shape), 2)

    calc_prob(data, labels, args)


if __name__ == "__main__":
    main(sys.argv[1:])
