# Project: VUT FIT SNT Project - Traveling Umpire Problem
# Author: Dominik Harmim <harmim6@gmail.com>
# Year: 2020
# Description: Functions for reading and parsing input files.

from os.path import abspath, dirname, exists
from re import search, split
from numpy import ndarray, array

IN_DIR = 'input'  # input directory


def get_inp_file(name: str) -> str:
    """
    Retrieves an input file name with a given problem.

    :param name: A name of an instance of the problem.
    :return: An input file name with a given problem.
    :raises: FileNotFoundError if an input file has not been found.
    """
    global IN_DIR

    file = abspath(dirname(__file__) + f'/../{IN_DIR}/{name}.txt')
    if not exists(file):
        raise FileNotFoundError

    return file


def parse_inp_file(file: str) -> (int, ndarray, ndarray):
    """
    Parses an input file.

    :param file: A name of an input file.
    :return: A tuple with a number of teams, distance matrix, and opponents
             matrix.
    """
    teams = 0
    dist = []
    opp = []

    match_teams = True
    match_dist = match_opp = False
    with open(file) as lines:
        for line in lines:
            if match_teams:
                s = search(r'nTeams\s*=\s*(\d+)\s*;', line)
                if s:
                    teams = int(s.group(1))
                    match_teams = False

            elif match_dist or match_opp:
                if search(r'\s*\]\s*;', line):
                    match_dist = match_opp = False
                else:
                    s = search(r'\[\s*(.*)\s*\]', line)
                    if s:
                        row = s.group(1).strip()
                        vals = [int(v) for v in split(r'\s+', row)]
                        dist.append(vals) if match_dist else opp.append(vals)

            elif search(r'dist\s*=\s*\[', line):
                match_dist = True

            elif search(r'opponents\s*=\s*\[', line):
                match_opp = True

    return teams, array(dist), array(opp)
