# Project: VUT FIT SNT Project - Traveling Umpire Problem
# Author: Dominik Harmim <harmim6@gmail.com>
# Year: 2020
# Description: An implementation of the greedy matching heuristic with the
#              Benders' cuts guided the neighbourhood search.

from tup import Tup
from random import randint
from itertools import combinations, permutations
from copy import deepcopy
from typing import Callable
from numpy import arange, zeros, int32, ones, where, ndarray, array_equal
from numpy.random import choice
from scipy.optimize import linear_sum_assignment

NEIGH_SEARCH_ITERS = 10_000  # limit of iterations in the neighbourhood search
NEIGH_SIZE = 2  # size of the umpire neighbourhood


def gmh(inp_file: str, d1: int, d2: int, name: str, time_limit: int) -> None:
    """
    The greedy matching heuristic algorithm. It reads an input instance of the
    Traveling Umpire Problem and produces a solution as optimal as possible. It
    tries to find a perfect match in every round. In the case that there is no
    feasible perfect match, the Benders' cuts are used to guide the large
    neighbourhood search heuristic.

    :param inp_file: A name of an input file.
    :param d1: The parameter d1 for 4. constraint.
    :param d2: The parameter d2 for 5. constraint.
    :param name: A name of an instance of the problem.
    :param time_limit: A time limit of the computation in minutes.
    """
    # initial solution
    tup = Tup(inp_file, d1, d2, name, time_limit)

    backtrack_constraint = zeros((tup.rounds, tup.umps * tup.umps), dtype=int32)
    prev_game_numbers = None

    # greedy matching for all rounds
    r = 1
    while r < tup.rounds:
        tup.time_limit_check()

        solutions = \
            tup.solutions_cart_product(tup.solution[:r], tup.solution[r:])

        distances = tup.umps_distances(solutions, r)
        r_distances = distances[r].reshape((tup.umps, tup.umps))

        constraint3 = tup.constraint3(solutions, r)
        constraint4 = tup.constraint4(solutions, r)
        constraint4_sum = constraint4.sum(axis=0)
        constraint5 = tup.constraint5(solutions, r)
        constraint5_sum = constraint5.sum(axis=0)
        constraints = \
            constraint3 + constraint4 + constraint5 + backtrack_constraint
        r_constraints = \
            constraints[r:].sum(axis=0).reshape((tup.umps, tup.umps))

        backtrack_constraint_sum = backtrack_constraint.sum(axis=0)
        backtrack_constraint = zeros(solutions.shape, dtype=int32)

        # perfect matching
        _, game_indexes = linear_sum_assignment(r_distances + r_constraints)
        game_numbers = game_indexes + arange(0, tup.umps * tup.umps, tup.umps)
        tup.solution = solutions[:, game_numbers]

        constraint_sums = \
            constraint4_sum[game_numbers] + constraint5_sum[game_numbers] \
            + backtrack_constraint_sum[game_numbers]
        # there is no perfect match
        if constraint_sums.sum():
            # try another initial solution if there is no perfect matching
            # in the first round
            if r == 1:
                tup.solution = tup.init_solution(tup.rounds, tup.umps)
                continue

            # backtracking
            if not tup.backtracked[r]:
                tup.backtracked[r] = True
                r -= 1
                backtrack_constraint[r, prev_game_numbers] = \
                    tup.penalty * tup.PENALTY
                continue

            # do the large neighbourhood search with the Benders' cuts
            cuts = benders_cuts(tup, r)
            if not cuts:
                continue
            tup = neigh_search(tup, r - 1, cuts)
            continue

        prev_game_numbers = deepcopy(game_numbers)
        print(f'Distance: {tup.umps_distances(tup.solution, r).sum()}')
        r += 1

    tup.print_solution()

    r = tup.rounds - 1
    calculate_score: Callable[[], int] = lambda: \
        tup.umps_distances(tup.solution, r).sum() \
        + tup.constraint3(tup.solution, r).sum()

    # try to improve a solution using the large neighbourhood search
    prev_score = calculate_score()
    while True:
        neigh_search(tup, r, [])

        score = calculate_score()
        if score < prev_score:
            print(f'Distance: {tup.umps_distances(tup.solution, r).sum()}')
            tup.print_solution()
        prev_score = score


def benders_cuts(tup: Tup, r: int) -> list:
    """
    Calculates the Benders' cuts in the round r.

    :param tup: The Traveling Umpire Problem instance.
    :param r: A round for which the Benders' cuts will be calculated.
    :return: The Benders' cuts in the round r.
    """
    venues = tup.venues_of_umps(tup.solution)
    out_venues = tup.venues_of_umps(tup.solution, home=False)

    # match matrix between umpires and games
    match = ones((tup.umps, tup.umps), dtype=int32)
    for i in range(0, tup.umps):
        for j in range(0, tup.umps):
            # 4. constraint
            for x in range(r - tup.q1 + 1, r):
                if venues[r, i] == venues[x, j]:
                    match[i, j] = 0
                    break

            # 5. constraint
            for x in range(r - tup.q2 + 1, r):
                if venues[r, i] == venues[x, j] \
                        or out_venues[r, i] == out_venues[x, j] \
                        or venues[r, i] == out_venues[x, j] \
                        or out_venues[r, i] == venues[x, j]:
                    match[i, j] = 0
                    break

    # find the Benders' cuts for all subsets of umpires
    cuts = []
    for length in range(1, tup.umps + 1):
        for umps in combinations(range(tup.umps), length):
            umps_card = len(umps)
            games = set()
            for ump in umps:
                games.update(set(where(match[:, ump])[0]))
            games_card = len(games)

            if games_card < umps_card:
                infeasible_games = set(range(0, tup.umps)) - games
                cut = []
                for i in infeasible_games:
                    for j in umps:
                        constraints = []

                        # 4. constraint
                        for x in range(r - tup.q1 + 1, r):
                            if venues[r, i] == venues[x, j]:
                                constraints.append((venues[x, j], x, j))

                        # 5. constraint
                        for x in range(r - tup.q2 + 1, r):
                            if venues[r, i] == venues[x, j] \
                                    or out_venues[r, i] == out_venues[x, j] \
                                    or venues[r, i] == out_venues[x, j] \
                                    or out_venues[r, i] == venues[x, j]:
                                constraints.append((venues[x, j], x, j))

                        cut.append(list(set(constraints)))
                cuts.append(cut)

    # find all permutations of the Benders' cuts
    cut_perms = []
    for cut in cuts:
        umps = []
        for constraints in cut:
            umps.append(constraints[0][2])

        for ump in permutations(umps):
            new_cut = []
            for c, constraint in enumerate(cut):
                new_constraint = []
                for venue, r, _ in constraint:
                    new_constraint.append((venue, r, ump[c]))
                new_cut.append(new_constraint)
            cut_perms.append(new_cut)

    return cut_perms


def benders_violations(venues: ndarray, cuts: list) -> int:
    """
    Calculates the number of violated Benders' cuts.

    :param venues: Home venues of umpires.
    :param cuts: The Benders' cuts for checking their violation.
    :return: The number of violated Benders' cuts.
    """
    violations = len(cuts)

    for cut in cuts:
        for constraints in cut:
            violated = False
            for venue, r, ump in constraints:
                if venues[r, ump] == venue:
                    violated = True
                    break
            if not violated:
                violations -= 1
                break

    return violations


def neigh_search(tup: Tup, r: int, cuts: list) -> Tup:
    """
    The very large neighbourhood search algorithm. It finds (partial) solution
    that satisfies constraints and all the Benders' cuts.

    :param tup: The Traveling Umpire Problem instance.
    :param r: A current round.
    :param cuts: The Benders' cuts that should be satisfied.
    :return: (Partial) solution that satisfies constraints and all the
             Benders' cuts.
    """
    global NEIGH_SEARCH_ITERS, NEIGH_SIZE

    prev_objective, _, _, _ = neigh_search_objective(tup, tup.solution, r, cuts)
    best_solution = deepcopy(tup.solution)
    n = 0
    while True:
        tup.time_limit_check()

        # try a new solution using a games swap
        solution = deepcopy(best_solution)
        umps = choice(arange(tup.umps), size=NEIGH_SIZE, replace=False)
        i = randint(0, r)
        ump_solution = solution[i, umps]
        while True:
            swap = choice(ump_solution, size=NEIGH_SIZE, replace=False)
            if not array_equal(ump_solution, swap):
                solution[i, umps] = swap
                break

        objective, constraint3, constraints45, violations = \
            neigh_search_objective(tup, solution, r, cuts)

        # updates the solution if the objective is improved
        if objective < prev_objective:
            n = 0
            best_solution = deepcopy(solution)
            prev_objective = objective

        # solution satisfies all conditions
        if not constraints45 and ((cuts and not violations)
                                  or (not cuts and not constraint3)):
            tup.solution = deepcopy(best_solution)
            return tup

        # test iterations limit
        n += 1
        if n == NEIGH_SEARCH_ITERS:
            n = 0
            best_solution = deepcopy(tup.solution)
            prev_objective, _, _, _ = \
                neigh_search_objective(tup, best_solution, r, cuts)


def neigh_search_objective(tup: Tup, solution: ndarray, r: int, cuts: list) \
        -> (int, int, int, int):
    """
    Calculates the objective function of the large neighbourhood search.

    :param tup: The Traveling Umpire Problem instance.
    :param solution: A solution for the calculation of the objective function.
    :param r: A current round.
    :param cuts: The Benders' cuts that should be satisfied.
    :return: A tuple with a value of the objective function, 3. constraint,
             4. and 5. constraint, and the number of Benders' cuts violations.
    """
    constraint3 = tup.constraint3(solution, r).sum()
    constraints45 = \
        tup.constraint4(solution, r).sum() + tup.constraint5(solution, r).sum()

    objective = \
        tup.umps_distances(solution, r).sum() + constraint3 + constraints45

    violations = 0
    if cuts:
        violations = benders_violations(tup.venues_of_umps(solution), cuts)
        objective += violations * tup.penalty * tup.PENALTY

    return objective, constraint3, constraints45, violations
