# Project: VUT FIT SNT Project - Traveling Umpire Problem
# Author: Dominik Harmim <harmim6@gmail.com>
# Year: 2020
# Description: An entry point of the application. It reads an input file and
#              executes the greedy matching heuristic.

from sys import argv, exit
from inp import get_inp_file
from tup import TimeLimitException
from gmh import gmh


ARGC = 5  # number of expected arguments

if __name__ == '__main__':
    if len(argv) != ARGC:
        print(f'Error: expecting {ARGC - 1} arguments:'
              f' {argv[0]} instance d1 d2 time-limit')
        exit(1)

    inp_file = ''
    try:
        inp_file = get_inp_file(argv[1])
    except FileNotFoundError:
        print(f"Error: an instance '{argv[1]}' has not been found.")
        exit(1)

    print(f"An instance '{inp_file}' has been found.\n")
    try:
        gmh(inp_file, int(argv[2]), int(argv[3]), argv[1], int(argv[4]))
    except TimeLimitException:
        print(f'\nThe time limit {argv[4]} minutes has been exceeded.')
    exit(0)
