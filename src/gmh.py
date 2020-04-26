# Project: VUT FIT SNT Project - Traveling Umpire Problem
# Author: Dominik Harmim <harmim6@gmail.com>
# Year: 2020
# Description: An entry point of the application. It reads an input file and
#              executes the greedy matching search.

from tup import Tup
from scipy.optimize import linear_sum_assignment
from numpy import arange, zeros, int32, ones, where, ndarray, array_equal
from numpy.random import choice
from copy import deepcopy
from itertools import combinations, permutations
from random import randint

NEIGH_SEARCH_ITERS = 10000
NEIGH_SIZE = 2


def gmh(inp_file: str, d1: int, d2: int, name: str, limit: int) -> None:
    """ Greedy matching heuristic. """

    # arbitrary assignment in the first slot
    tup = Tup(inp_file, d1, d2, name)
    backtrack_constraint = zeros((tup.rounds, tup.umps * tup.umps), dtype=int32)
    prev_game_numbers = None

    r = 1
    while r < tup.rounds:
        solutions = tup.solutions_cart_product(
            tup.solution[:r, :], tup.solution[r:, :])
        distances = tup.umps_distances(solutions, r)
        constraint3 = tup.constraint3(solutions, r)
        constraint4 = tup.constraint4(solutions, r)
        constraint4_sum = constraint4.sum(axis=0)
        constraint5 = tup.constraint5(solutions, r)
        constraint5_sum = constraint5.sum(axis=0)
        constraints = constraint3 + constraint4 + constraint5

        backtrack_constraint_sum = backtrack_constraint.sum(axis=0)
        constraints += backtrack_constraint
        backtrack_constraint = zeros(solutions.shape, dtype=int32)

        r_distances = distances[r, :].reshape((tup.umps, tup.umps))
        r_constraints = \
            constraints[r:, :].sum(axis=0).reshape((tup.umps, tup.umps))

        # perfect matching
        game_indexes = linear_sum_assignment(r_distances + r_constraints)[1]
        game_numbers = game_indexes + arange(0, tup.umps * tup.umps, tup.umps)

        tup.solution = solutions[:, game_numbers]

        constraint_sums = \
            constraint4_sum[game_numbers] + constraint5_sum[game_numbers] \
            + backtrack_constraint_sum[game_numbers]
        if constraint_sums.sum() > 0:
            if r == 1 and prev_game_numbers is None:
                tup.solution = tup.init_solution(tup.rounds, tup.umps)
                continue

            # backtracking
            if not tup.backtracked[r]:
                tup.backtracked[r] = True
                r -= 1
                backtrack_constraint[r, prev_game_numbers] = \
                    tup.penalty * tup.PENALTY
                continue
            else:
                cuts = benders_cuts(tup, r)
                if not cuts:
                    continue
                tup = neigh_search(tup, r - 1, cuts)
                continue

        prev_game_numbers = deepcopy(game_numbers)
        print('Dis: {0}'.format(tup.umps_distances(tup.solution, r).sum()))
        r += 1

    tup.print_solution()

    r = tup.rounds - 1
    total_travel = tup.umps_distances(tup.solution, r).sum()
    constraint3 = tup.constraint3(tup.solution, r).sum()
    prev_score = total_travel + constraint3

    while True:
        neigh_search(tup, r, [])

        total_travel = tup.umps_distances(tup.solution, r).sum()
        constraint3 = tup.constraint3(tup.solution, r).sum()
        score = total_travel + constraint3
        if score < prev_score:
            print('Dis: {0}'.format(tup.umps_distances(tup.solution, r).sum()))
            tup.print_solution()
        prev_score = score


def benders_cuts(tup: Tup, r: int) -> list:
    cuts = []
    venues = tup.venues_of_umps(tup.solution)
    out_venues = tup.venues_of_umps(tup.solution, home=False)

    match = ones((tup.umps, tup.umps), dtype=int32)
    for i in range(0, tup.umps):
        for j in range(0, tup.umps):
            for x in range(r - tup.q1 + 1, r):
                if venues[r, i] == venues[x, j]:
                    match[i, j] = 0
                    break

            for x in range(r - tup.q2 + 1, r):
                if venues[r, i] == venues[x, j] \
                        or out_venues[r, i] == out_venues[x, j] \
                        or venues[r, i] == out_venues[x, j] \
                        or out_venues[r, i] == venues[x, j]:
                    match[i, j] = 0
                    break

    for length in range(1, tup.umps + 1):
        for umps in set(combinations(set(range(tup.umps)), length)):
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
                        constraint = []

                        for x in range(r - tup.q1 + 1, r):
                            if venues[r, i] == venues[x, j]:
                                constraint.append((venues[x, j], x, j))

                        for x in range(r - tup.q2 + 1, r):
                            if venues[r, i] == venues[x, j] \
                                    or out_venues[r, i] == out_venues[x, j] \
                                    or venues[r, i] == out_venues[x, j] \
                                    or out_venues[r, i] == venues[x, j]:
                                constraint.append((venues[x, j], x, j))

                        cut.append(list(set(constraint)))
                cuts.append(cut)

    cut_perms = []
    for cut in cuts:
        umps = []
        for constraints in cut:
            umps.append(constraints[0][2])
        for ump in list(permutations(umps)):
            new_cut = []
            for c in range(0, len(cut)):
                constraint = []
                for venue, r, _ in cut[c]:
                    constraint.append((venue, r, ump[c]))
                new_cut.append(constraint)
            cut_perms.append(new_cut)
    cuts = cut_perms

    return cuts


def benders_violations(venues: ndarray, cuts: list) -> int:
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
    global NEIGH_SEARCH_ITERS, NEIGH_SIZE

    total_travel = tup.umps_distances(tup.solution, r).sum()
    constraint3 = tup.constraint3(tup.solution, r).sum()
    constraint4 = tup.constraint4(tup.solution, r).sum()
    constraint5 = tup.constraint5(tup.solution, r).sum()
    prev_objective = total_travel + constraint3 + constraint4 + constraint5
    if cuts:
        violations = benders_violations(tup.venues_of_umps(tup.solution), cuts)
        prev_objective += violations * tup.penalty * tup.PENALTY

    best_solution = deepcopy(tup.solution)
    k = NEIGH_SIZE
    n = 0
    while True:
        solution = deepcopy(best_solution)
        umps = choice(arange(tup.umps), size=k, replace=False)
        i = randint(0, r)
        ump_solution = solution[i, umps]
        while True:
            swap = choice(ump_solution, size=k, replace=False)
            if not array_equal(ump_solution, swap):
                solution[i, umps] = swap
                break

        total_travel = tup.umps_distances(solution, r).sum()
        constraint3 = tup.constraint3(solution, r).sum()
        constraint4 = tup.constraint4(solution, r).sum()
        constraint5 = tup.constraint5(solution, r).sum()
        constraints45 = constraint4 + constraint5
        objective = total_travel + constraint3 + constraints45
        violations = 0
        if cuts:
            violations = benders_violations(tup.venues_of_umps(solution), cuts)
            objective += violations * tup.penalty * tup.PENALTY

        if objective < prev_objective:
            n = 0
            best_solution = deepcopy(solution)
            prev_objective = objective

        if not constraints45 and ((cuts and not violations) or (not cuts and not constraint3)):
            tup.solution = deepcopy(best_solution)
            return tup

        n += 1
        if n == NEIGH_SEARCH_ITERS:
            n = 0
            best_solution = deepcopy(tup.solution)

            total_travel = tup.umps_distances(best_solution, r).sum()
            constraint3 = tup.constraint3(best_solution, r).sum()
            constraint4 = tup.constraint4(best_solution, r).sum()
            constraint5 = tup.constraint5(best_solution, r).sum()
            prev_objective = \
                total_travel + constraint3 + constraint4 + constraint5
            if cuts:
                violations = \
                    benders_violations(tup.venues_of_umps(best_solution), cuts)
                prev_objective += violations * tup.penalty * tup.PENALTY
