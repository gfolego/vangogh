#!/usr/bin/python

# classify.py
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
Classification
============================================================

Classification using grid search with cross-validation

"""


import sys
import argparse
from multiprocessing import cpu_count
import numpy as np
from sklearn import svm, grid_search, cross_validation, metrics
import cPickle as pickle

from common import CACHE_SIZE, C_RANGE, GAMMA_RANGE, CLASS_WEIGHTS, N_ITER, K_FOLD, \
    iter_type, dir_type, print_verbose, set_verbose_level, get_verbose_level, get_n_cores, set_n_cores

from gather_data import gen_data, parse_class


def eval_perf(classification):
    y_true = []
    y_pred = []

    for (key, value) in classification.iteritems():
        y_true.extend([parse_class(key)])
        y_pred.extend([value])

        print_verbose("Classification pair: %s" % str((key, value)), 4)
        print_verbose("True classes: %s" % str(y_true), 5)
        print_verbose("Predicted classes: %s" % str(y_pred), 5)

    # Print metrics
    print_verbose("Confusion Matrix:", 0)
    print_verbose(metrics.confusion_matrix(y_true, y_pred), 0)
    print_verbose("Classification Report:", 0)
    print_verbose(metrics.classification_report(y_true, y_pred), 0)


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-d', '--dir', type=dir_type, required=True,
                        help='data directory')
    parser.add_argument('-v', '--verbose', action='count',
                        help='verbosity level')
    parser.add_argument('-c', '--cores', default=get_n_cores(), type=int,
                        choices=xrange(1, cpu_count()+1),
                        help='number of cores to be used (default: %d)' % get_n_cores())
    parser.add_argument('-m', '--model', type=str, required=True,
                        help='path to import the classifier model')
    parser.add_argument('-p', '--prob', action='count', default=0,
                        help='use distance from margin (# is aggregation method')


    args = parser.parse_args(args=argv)
    return args


def aggregate_predictions(pred):
    print_verbose('Aggregating using mode ...', 0)
    counts = np.bincount(pred)
    return np.argmax(counts)

def agg_pred_dist_sumall(pred, classes):
    print_verbose('Aggregating by summing all distances ...', 0)
    tot = np.sum(pred)
    cl = classes[1] if (tot > 0) else classes[0]
    return cl

def agg_pred_dist_far(pred, classes):
    print_verbose('Aggregating by using the farthest point class ...', 0)

    arr_pos = pred[pred >= 0]
    max_pos = np.max(arr_pos) if (arr_pos.size > 0) else 0

    arr_neg = pred[pred <= 0]
    max_neg = np.abs(np.min(arr_neg)) if (arr_neg.size > 0) else 0

    cl = classes[1] if (max_pos > max_neg) else classes[0]
    return cl

def agg_pred_dist_meangroup(pred, classes):
    print_verbose('Aggregating by comparing distance groups means ...', 0)

    arr_pos = pred[pred >= 0]
    avg_pos = np.mean(arr_pos) if (arr_pos.size > 0) else 0

    arr_neg = pred[pred <= 0]
    avg_neg = np.abs(np.mean(arr_neg)) if (arr_neg.size > 0) else 0

    cl = classes[1] if (avg_pos > avg_neg) else classes[0]
    return cl

def agg_pred_dist_mediangroup(pred, classes):
    print_verbose('Aggregating by comparing distance groups means ...', 0)

    arr_pos = pred[pred >= 0]
    med_pos = np.median(arr_pos) if (arr_pos.size > 0) else 0

    arr_neg = pred[pred <= 0]
    med_neg = np.abs(np.median(arr_neg)) if (arr_neg.size > 0) else 0

    cl = classes[1] if (med_pos > med_neg) else classes[0]
    return cl



def classify(data, labels, classes, args):

    classification = {}

    # Read model
    with open(args.model, "rb") as f:
        model = pickle.load(f)
    print_verbose("Model [%0.2f%%]: %s" % (model.best_score_*100, str(model.best_estimator_)), 4)


    # Classify each label
    lolo = cross_validation.LeaveOneLabelOut(labels)
    print_verbose("LeaveOneOut: %s" % str(lolo), 5)

    for train_index, test_index in lolo:
        print_verbose("Test index: %s" % str(test_index), 5)
        print_verbose("Classifying label: %s" % str(labels[test_index[0]]), 4)

        # Classify
        if args.prob is 0:
            pred = model.predict(data[test_index])
        else:
            pred = model.decision_function(data[test_index])
        print_verbose("Patch prediction: %s" % str(pred), 4)

        # Aggregate
        if args.prob is 0:
            res = aggregate_predictions(pred)
        elif args.prob is 1:
            res = agg_pred_dist_sumall(pred, model.best_estimator_.classes_)
        elif args.prob is 2:
            res = agg_pred_dist_far(pred, model.best_estimator_.classes_)
        elif args.prob is 3:
            res = agg_pred_dist_meangroup(pred, model.best_estimator_.classes_)
        elif args.prob is 4:
            res = agg_pred_dist_mediangroup(pred, model.best_estimator_.classes_)
        print_verbose("Aggregate result: %s" % str(res), 4)

        # Append to final result
        classification[labels[test_index[0]]] = res
        print_verbose("Classification: %s" % str(classification), 5)

    return classification


def main(argv):

    # Parse arguments
    args = parse_args(argv)
    set_verbose_level(args.verbose)
    set_n_cores(args.cores)

    print_verbose("Args: %s" % str(args), 1)

    # Some tests
    data, labels, classes = gen_data(args.dir)
    print_verbose('Data: %s' % str(data), 5)
    print_verbose('Labels: %s' % str(labels), 4)
    print_verbose('Classes: %s' % str(classes), 4)

    print_verbose('Data shape: %s' % str(data.shape), 2)
    print_verbose('Labels shape: %s' % str(labels.shape), 2)
    print_verbose('Classes shape: %s' % str(classes.shape), 2)

    classification = classify(data, labels, classes, args)
    print_verbose('Final classification: %s' % str(classification), 0)

    # Evaluate performance
    eval_perf(classification)


if __name__ == "__main__":
    main(sys.argv[1:])
