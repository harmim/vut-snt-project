# Project: VUT FIT SNT Project - Traveling Umpire Problem
# Author: Dominik Harmim <harmim6@gmail.com>
# Year: 2020
# Description: A definition of a class that represents the
#              Traveling Umpire Problem.

from inp import parse_inp_file
from out import print_solution
from datetime import datetime
from numpy import ndarray, arange, tile, where, zeros, int32, unique, roll
from numpy.random import choice


class TimeLimitException(Exception):
    """ An exception that represents the time limit overrun. """
    pass


class Tup:
    """ A class that represents the Traveling Umpire Problem. """

    PENALTY = 1_000  # implicit value of a penalty

    def __init__(self, inp_file: str, d1: int, d2: int, name: str,
                 time_limit: int) -> None:
        """
        Constructs the Traveling Umpire Problem.

        :param inp_file: A name of an input file.
        :param d1: The parameter d1 for 4. constraint.
        :param d2: The parameter d2 for 5. constraint.
        :param name: A name of an instance of the problem.
        :param time_limit: A time limit of the computation in minutes.
        """
        super().__init__()

        self.__name = name
        self.__teams, self.__dist, opp = parse_inp_file(inp_file)
        self.__umps = int(self.__teams / 2)
        self.__schedule = self.__build_schedule(opp)
        self.__rounds = self.__schedule.shape[0]
        self.__q1 = self.umps - d1
        self.__q2 = int(self.umps / 2) - d2
        self.__penalty = self.umps * self.PENALTY
        self.solution = self.init_solution(self.rounds, self.umps)
        self.__backtracked = [True] + [False] * (self.rounds - 1)
        self.__time_limit = time_limit
        self.__time = datetime.now()

    @property
    def umps(self) -> int:
        """
        Returns the number of umpires.

        :return: The number of umpires.
        """
        return self.__umps

    @property
    def rounds(self) -> int:
        """
        Returns the number of rounds.

        :return: The number of rounds.
        """
        return self.__rounds

    @property
    def q1(self) -> int:
        """
        Returns the parameter q1 for 4. constraint.

        :return: The parameter q1 for 4. constraint.
        """
        return self.__q1

    @property
    def q2(self) -> int:
        """
        Returns the parameter q2 for 5. constraint.

        :return: The parameter q2 for 5. constraint.
        """
        return self.__q2

    @property
    def penalty(self) -> int:
        """
        Returns a defined value of a penalty.

        :return: A defined value of a penalty.
        """
        return self.__penalty

    @property
    def solution(self) -> ndarray:
        """
        Returns a (partial) solution of the problem.

        :return: A (partial) solution of the problem.
        """
        return self.__solution

    @solution.setter
    def solution(self, solution: ndarray) -> None:
        """
        Updates a solution of the problem.

        :param solution: A new solution of the problem.
        """
        self.__solution = solution

    @property
    def backtracked(self) -> list:
        """
        Returns a list of flags with realised backtracks in single rounds.

        :return: A list of flags with realised backtracks in single rounds.
        """
        return self.__backtracked

    def time_limit_check(self) -> None:
        """
        Raises an exception if a time limit is exceeded.

        :raises: TimeLimitException if a time limit is exceeded.
        """
        duration = (datetime.now() - self.__time).total_seconds() // 60
        if duration >= self.__time_limit:
            raise TimeLimitException

    @staticmethod
    def __build_schedule(opp: ndarray) -> ndarray:
        """
        Builds a schedule of the tournament.

        :param opp: An opponents matrix.
        :return: A built schedule matrix of the tournament.
        """
        rounds, teams = opp.shape
        games = int(teams / 2)
        schedule_shape = rounds, games

        team_indexes = tile(arange(teams), (rounds, 1))
        home_games = (team_indexes[where(opp > 0)] + 1).reshape(schedule_shape)
        out_games = opp[opp > 0].reshape(schedule_shape)

        schedule = zeros((rounds, games, 2), dtype=int32)
        schedule[:, :, 0] = home_games
        schedule[:, :, 1] = out_games

        return schedule

    @staticmethod
    def init_solution(rounds: int, umps: int) -> ndarray:
        """
        Returns an initial solution (a solution of the first round).

        :param rounds: The number of rounds.
        :param umps: The number of umpires.
        :return: An initial solution (a solution of the first round).
        """
        solution = zeros((rounds, umps), dtype=int32)

        ump_indexes = arange(umps)
        for r in range(rounds):
            solution[r] = choice(ump_indexes, size=umps, replace=False) + 1

        return solution

    def print_solution(self) -> None:
        """
        Prints the solution.
        """
        r = self.rounds - 1
        constraints = \
            self.constraint3(self.solution, r) \
            + self.constraint4(self.solution, r) \
            + self.constraint5(self.solution, r)
        feasibility = 'Infeasible' if constraints.sum() else 'Feasible'
        print(f'\n{feasibility} solution:')

        solution = zeros(self.solution.shape, dtype=int32)
        game_numbers = arange(self.umps) + 1
        game_matrix = tile(game_numbers, (self.rounds, 1))
        for game in game_numbers:
            solution[:, game - 1] = game_matrix[where(self.solution == game)]
        print_solution(','.join(map(str, solution.flatten())), self.__name)

    def venues_of_umps(self, solution: ndarray, home=True) -> ndarray:
        """
        Returns either home or out venues of umpires, according to 'home' flag.

        :param solution: A solution for which the venues are returned.
        :param home: A flag to determine whether return home or out venues.
        :return: Either home or out venues of umpires, according to 'home' flag.
        """
        games = self.__schedule[:, :, 0 if home else 1]
        rounds, umps = solution.shape
        rows = tile(arange(rounds).reshape((rounds, 1)), (1, umps))

        return games[rows, solution - 1]

    def umps_distances(self, solution: ndarray, curr_round: int) -> ndarray:
        """
        Returns distances for umpires in single rounds.

        :param solution: A solution for which the distances are returned.
        :param curr_round: A current round.
        :return: Distances for umpires in single rounds.
        """
        venues = self.venues_of_umps(solution) - 1
        distances = zeros(venues.shape, dtype=int32)

        for r in range(1, curr_round + 1):
            distances[r] = self.__dist[venues[r - 1], venues[r]]

        return distances

    @staticmethod
    def solutions_cart_product(s1: ndarray, s2: ndarray) -> ndarray:
        """
        Calculates the Cartesian product of two given solutions.

        :param s1: The first argument for the product.
        :param s2: The second argument for the product.
        :return: The Cartesian product of two given solutions.
        """
        rounds, umps = s1.shape
        product = zeros((rounds + s2.shape[0], umps * umps), dtype=int32)

        for x in range(umps):
            for y in range(umps):
                col = x * umps + y
                product[:rounds, col] = s1[:, x]
                product[rounds:, col] = s2[:, y]

        return product

    def constraint3(self, solution: ndarray, curr_round: int) -> ndarray:
        """
        3. constraint: Every umpire sees every team at least once at team's
                       home.

        :param solution: A solution for calculating 3. constraint.
        :param curr_round: A current round.
        :return: A matrix with penalties where assignment violates
                 3. constraint.
        """
        venues = self.venues_of_umps(solution)
        constraint = zeros(venues.shape, dtype=int32)

        venue_numbers = arange(1, self.__teams + 1)
        for venue in range(venues.shape[1]):
            unvisit_venues = \
                set(venue_numbers) - set(unique(venues[:curr_round + 1, venue]))
            for _ in unvisit_venues:
                constraint[-1, venue] += self.penalty

        return constraint

    def constraint4(self, solution: ndarray, curr_round: int) -> ndarray:
        """
        4. constraint: No umpire is in the same venue more than once in any
                       q1 consecutive rounds.

        :param solution: A solution for calculating 4. constraint.
        :param curr_round: A current round.
        :return: A matrix with penalties where assignment violates
                 4. constraint.
        """
        constraint = zeros(solution.shape, dtype=int32)

        if self.q1 > 1:
            venues = self.venues_of_umps(solution)
            rolled = venues

            for _ in range(1, self.q1):
                rolled = roll(rolled, 1, axis=0)
                rolled[0] = -1
                constraint += (venues == rolled).astype(int)

            constraint[curr_round + 1:] = 0

        constraint *= self.penalty * self.PENALTY

        return constraint

    def constraint5(self, solution: ndarray, curr_round: int) -> ndarray:
        """
        5. constraint: No umpire sees a team more than once in any q2
                       consecutive rounds.

        :param solution: A solution for calculating 5. constraint.
        :param curr_round: A current round.
        :return: A matrix with penalties where assignment violates
                 5. constraint.
        """
        constraint = zeros(solution.shape, dtype=int32)

        if self.q2 > 1:
            venues = self.venues_of_umps(solution)
            rolled = venues
            out_venues = self.venues_of_umps(solution, home=False)
            out_rolled = out_venues

            for _ in range(1, self.q2):
                rolled = roll(rolled, 1, axis=0)
                rolled[0] = -1
                out_rolled = roll(out_rolled, 1, axis=0)
                out_rolled[0] = -1
                constraint += \
                    (venues == rolled).astype(int) \
                    + (venues == out_rolled).astype(int) \
                    + (out_venues == rolled).astype(int) \
                    + (out_venues == out_rolled).astype(int)

            constraint[curr_round + 1:] = 0

        constraint *= self.penalty * self.PENALTY

        return constraint
