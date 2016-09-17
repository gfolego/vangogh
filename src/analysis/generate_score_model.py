#!/usr/bin/python

# generate_score_model.py
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
Generate score model
============================================================

Generate score transformation model with cross-validation

"""


import sys
import argparse
from multiprocessing import cpu_count
import numpy as np
from sklearn import linear_model, grid_search, cross_validation
import cPickle as pickle

from common import CACHE_SIZE, C_RANGE, CLASS_WEIGHTS, \
    SCORE_MAX_ITER, SCORE_K_FOLD, \
    dir_type, print_verbose, set_verbose_level, get_verbose_level, get_n_cores, set_n_cores

from gather_data import gen_data


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-d', '--dir', type=dir_type, required=True,
                        help='data directory')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='verbosity level')
    parser.add_argument('-c', '--cores', default=int(cpu_count()-2), type=int,
                        choices=xrange(1, cpu_count()+1),
                        help='number of cores to be used (default: %d)' % int(cpu_count()-2))
    parser.add_argument('-m', '--model', type=str, required=True,
                        help='path to import the classifier model')
    parser.add_argument('-s', '--score', type=str, required=True,
                        help='path to export the score model')


    args = parser.parse_args(args=argv)
    return args


def generate_model(data, classes, args):

    # Define the parameters
    tuned_parameters = {'C': C_RANGE,
                        'class_weight': CLASS_WEIGHTS}

    # Define the classifier
    clf = linear_model.LogisticRegression(max_iter=SCORE_MAX_ITER, n_jobs=args.cores)

    print_verbose("Classifier: %s" % str(clf), 5)
    print_verbose("Parameters: %s" % str(tuned_parameters), 5)

    # Generate the K-fold development
    skf = cross_validation.StratifiedKFold(classes, n_folds=SCORE_K_FOLD, shuffle=True)
    print_verbose("KFold: %s" % str(skf), 5)

    gscv = grid_search.GridSearchCV(clf, tuned_parameters, cv=skf,
                                    scoring='mean_squared_error',
                                    n_jobs=1, verbose=get_verbose_level())

    # Search
    print_verbose("GridSearch: %s" % str(gscv), 5)
    gscv.fit(data, classes)

    # Print scores
    print_verbose("GridSearch scores:", 5)
    for params, mean_score, scores in gscv.grid_scores_:
        print_verbose("%0.6f (+/-%0.06f) for %r"
                      % (mean_score, scores.std() / 2, params), 5)

    # Print best score
    print_verbose("GridSearch best score:", 0)
    print_verbose("%0.6f for %r" % (gscv.best_score_, gscv.best_params_), 0)

    return gscv


def calc_dist(clf_model, data):

    # Read model
    with open(clf_model,  "rb") as f:
        model = pickle.load(f)
    print_verbose("Model [%0.2f%%]: %s" % (model.best_score_*100, str(model.best_estimator_)), 4)

    # Calculate distances
    dist = model.decision_function(data)
    dist = dist.reshape(-1, 1)

    return dist


def main(argv):

    # Parse arguments
    args = parse_args(argv)
    set_verbose_level(args.verbose)
    set_n_cores(args.cores)

    print_verbose("Args: %s" % str(args), 1)

    # Prepare data
    data, labels, classes = gen_data(args.dir)
    print_verbose('Data: %s' % str(data), 5)
    print_verbose('Labels: %s' % str(labels), 4)
    print_verbose('Classes: %s' % str(classes), 4)

    print_verbose('Data shape: %s' % str(data.shape), 2)
    print_verbose('Labels shape: %s' % str(labels.shape), 2)
    print_verbose('Classes shape: %s' % str(classes.shape), 2)

    print_verbose('Data bytes: %s' % str(data.nbytes), 2)

    # Calculate distances
    dist = calc_dist(args.model, data)

    # Generate score model
    model = generate_model(dist, classes, args)
    print_verbose('Model: %s' % str(model), 0)

    # Export
    print_verbose('Saving model to %s' % args.score, 0)
    with open(args.score, "wb") as f:
        pickle.dump(model, f)

    print_verbose('Done!', 0)


if __name__ == "__main__":
    main(sys.argv[1:])
