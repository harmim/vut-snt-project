from os.path import abspath, dirname, exists
from numpy import ndarray, array
from re import search, split


def get_inp_file(name: str) -> str:
    file = abspath(dirname(__file__) + '/../input/{0}.txt'.format(name))
    if not exists(file):
        raise FileNotFoundError

    return file


def parse_inp_file(file: str) -> (int, ndarray, ndarray):
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
                        arr = [int(x) for x in split(r'\s+', row)]
                        if match_dist:
                            dist.append(arr)
                        else:
                            opp.append(arr)

            elif search(r'dist\s*=\s*\[', line):
                match_dist = True

            elif search(r'opponents\s*=\s*\[', line):
                match_opp = True

    return teams, array(dist), array(opp)
