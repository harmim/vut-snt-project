# Project: VUT FIT SNT Project - Traveling Umpire Problem
# Author: Dominik Harmim <harmim6@gmail.com>
# Year: 2020
# Description: An entry point of the application. It reads an input file and
#              executes the greedy matching heuristic.

from sys import argv, exit
from inp import get_inp_file
from gmh import gmh


ARGC = 5  # a number of expected arguments

if __name__ == '__main__':
    if len(argv) != ARGC:
        print('Error: expecting {0} arguments: {1} instance d1 d2 time-limit'
              .format(ARGC - 1, argv[0]))
        exit(1)

    inp_file = ''
    try:
        inp_file = get_inp_file(argv[1])
    except FileNotFoundError:
        print("Error: an instance '{0}' has not been found.".format(argv[1]))
        exit(1)

    print("An instance '{0}' has been found.\n".format(inp_file))
    gmh(inp_file, int(argv[2]), int(argv[3]), argv[1], int(argv[4]))
    exit(0)
