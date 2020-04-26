# Project: VUT FIT SNT Project - Traveling Umpire Problem
# Author: Dominik Harmim <harmim6@gmail.com>
# Year: 2020
# Description: Functions for writing solutions to output files.

from os import makedirs
from os.path import abspath, dirname, exists

OUT_DIR = 'output'  # output directory


def print_solution(solution: str, name: str, q1: int, q2: int) -> None:
    """
    Prints a solution to an output file and to the standard output.

    :param solution: A solution to be printed.
    :param name: A name of an instance of the problem.
    :param q1: The parameter q1 for 4. constraint.
    :param q2: The parameter q2 for 5. constraint.
    """
    global OUT_DIR

    out_dir = abspath(dirname(__file__) + f'/../{OUT_DIR}')
    if not exists(out_dir):
        makedirs(out_dir)

    with open(out_dir + f'/{name}-{q1}-{q2}.txt', 'w') as f:
        print(solution, file=f)
    print(f'{solution}\n')
