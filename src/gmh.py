from tup import Tup
from scipy.optimize import linear_sum_assignment
from numpy import arange, zeros, int32


def gmh(inp_file: str, d1: int, d2: int, name: str) -> None:
    """ Greedy matching heuristic. """

    # arbitrary assignment in the first slot
    tup = Tup(inp_file, d1, d2, name)
    backtrack_constraint = zeros((tup.rounds, tup.umps * tup.umps), dtype=int32)
    prev_game_numbers = None

    r = 1
    while r < tup.rounds:
        solutions = tup.solutions_cross_product(
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

        constraint_sums = \
            constraint4_sum[game_numbers] + constraint5_sum[game_numbers] \
            + backtrack_constraint_sum[game_numbers]
        if constraint_sums.sum() > 0:
            # backtracking
            if not tup.backtracked[r]:
                tup.backtracked[r] = True

                if r == 1 and prev_game_numbers is None:
                    tup.solution = tup.init_solution(tup.rounds, tup.umps)
                else:
                    r -= 1
                    backtrack_constraint[r, prev_game_numbers] = \
                        tup.penalty * tup.PENALTY

                continue

            else:
                raise Exception

        tup.solution = solutions[:, game_numbers]

        prev_game_numbers = game_numbers
        r += 1

    tup.print_solution()
