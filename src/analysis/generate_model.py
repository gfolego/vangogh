#!/usr/bin/python

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



def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-k', '--kernel', type=str, choices=['linear', 'rbf'], default='linear',
                        help='SVM kernel (default: linear)')
    parser.add_argument('-s', '--search', type=str, choices=['grid', 'random'], default='random',
                        help='search mode (default: random)')
    parser.add_argument('-i', '--iter', default=N_ITER, type=iter_type,
                        help='number of iterations for random search (default: %d)' % N_ITER)
    parser.add_argument('-d', '--dir', type=dir_type, required=True,
                        help='data directory')
    parser.add_argument('-v', '--verbose', action='count',
                        help='verbosity level')
    parser.add_argument('-c', '--cores', default=int(cpu_count()-2), type=int,
                        choices=xrange(1, cpu_count()+1),
                        help='number of cores to be used (default: %d)' % int(cpu_count()-2))
    parser.add_argument('-m', '--model', type=str, required=True,
                        help='path to export the generated model')


    args = parser.parse_args(args=argv)
    return args


def aggregate_predictions(pred):
    counts = np.bincount(pred)
    return np.argmax(counts)


def generate_model(data, classes, args):

    # Define the parameters
    tuned_parameters = {'C': C_RANGE,
                        'class_weight': CLASS_WEIGHTS}

    # Define the classifier
    if args.kernel == 'rbf':
        clf = svm.SVC(cache_size=CACHE_SIZE)
        tuned_parameters['gamma'] = GAMMA_RANGE
    else:
        clf = svm.LinearSVC(dual=False)

    print_verbose("Classifier: %s" % str(clf), 5)
    print_verbose("Parameters: %s" % str(tuned_parameters), 5)

    # Generate the K-fold development
    skf = cross_validation.StratifiedKFold(classes, n_folds=K_FOLD, shuffle=True)
    print_verbose("KFold: %s" % str(skf), 5)

    # Generate the grid search
    if args.search == 'grid':
        gscv = grid_search.GridSearchCV(clf, tuned_parameters, cv=skf, scoring='f1',
                                        n_jobs=1, verbose=get_verbose_level())
    else:
        gscv = grid_search.RandomizedSearchCV(clf, tuned_parameters, cv=skf, scoring='f1',
                                              n_jobs=1, verbose=get_verbose_level(), n_iter=args.iter)

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


def main(argv):

    # Parse arguments
    args = parse_args(argv)
    set_verbose_level(args.verbose)
    set_n_cores(args.cores)

    print_verbose("Args: %s" % str(args), 1)

    # Training
    data, labels, classes = gen_data(args.dir)
    print_verbose('Data: %s' % str(data), 5)
    print_verbose('Labels: %s' % str(labels), 4)
    print_verbose('Classes: %s' % str(classes), 4)

    print_verbose('Data shape: %s' % str(data.shape), 2)
    print_verbose('Labels shape: %s' % str(labels.shape), 2)
    print_verbose('Classes shape: %s' % str(classes.shape), 2)

    print_verbose('Data bytes: %s' % str(data.nbytes), 2)

    model = generate_model(data, classes, args)
    print_verbose('Model: %s' % str(model), 0)

    # Export
    print_verbose('Saving model to %s' % args.model, 0)
    with open(args.model, "wb") as f:
        pickle.dump(model, f)

    print_verbose('Done!', 0)


if __name__ == "__main__":
    main(sys.argv[1:])
