from os import makedirs
from os.path import abspath, dirname, exists


def print_solution(solution: str, name: str) -> None:
    out_dir = abspath(dirname(__file__) + '/../output/{0}/'.format(name))
    if not exists(out_dir):
        makedirs(out_dir)

    with open(out_dir + '/solution.txt', 'w') as f:
        print(solution, file=f)
