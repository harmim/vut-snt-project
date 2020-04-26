# Project: VUT FIT SNT Project - Traveling Umpire Problem
# Author: Dominik Harmim <harmim6@gmail.com>
# Year: 2020
# Description: Functions for writing solutions to output files.

from os import makedirs
from os.path import abspath, dirname, exists

OUT_DIR = 'output'  # an output directory


def print_solution(solution: str, name: str) -> None:
    """
    Prints a solution to an output file and to the standard output.

    :param solution: A solution to be printed.
    :param name: A name of an instance of the problem.
    """
    global OUT_DIR

    out_dir = abspath(dirname(__file__) + '/../{0}'.format(OUT_DIR))
    if not exists(out_dir):
        makedirs(out_dir)

    with open(out_dir + '/{0}.txt'.format(name), 'w') as f:
        print(solution, file=f)
    print(solution)
