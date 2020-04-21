from inp import parse_inp_file
from numpy import ndarray, arange, tile, where, zeros, int32, unique, roll
from numpy.random import choice
from out import print_solution


class Tup:
    PENALTY = 1000

    def __init__(self, inp_file: str, d1: int, d2: int, name: str) -> None:
        super().__init__()

        self.name = name
        self.teams, self.dist, opp = parse_inp_file(inp_file)
        self.umps = self.teams // 2
        self.schedule, self.home_games = self.__build_schedule(opp)
        self.rounds = self.schedule.shape[0]
        self.c4 = self.umps - d1
        self.c5 = self.umps // 2 - d2
        self.penalty = self.umps * self.PENALTY
        self.solution = self.init_solution(self.rounds, self.umps)
        self.backtracked = [True] + [False] * (self.rounds - 1)

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str) -> None:
        self.__name = name

    @property
    def teams(self) -> int:
        return self.__teams

    @teams.setter
    def teams(self, teams: int) -> None:
        self.__teams = teams

    @property
    def dist(self) -> ndarray:
        return self.__dist

    @dist.setter
    def dist(self, dist: ndarray) -> None:
        self.__dist = dist

    @property
    def umps(self) -> int:
        return self.__umps

    @umps.setter
    def umps(self, umps: int) -> None:
        self.__umps = umps

    @property
    def schedule(self) -> ndarray:
        return self.__schedule

    @schedule.setter
    def schedule(self, schedule: ndarray) -> None:
        self.__schedule = schedule

    @property
    def home_games(self) -> dict:
        return self.__home_games

    @home_games.setter
    def home_games(self, home_games: dict) -> None:
        self.__home_games = home_games

    @property
    def rounds(self) -> int:
        return self.__rounds

    @rounds.setter
    def rounds(self, rounds: int) -> None:
        self.__rounds = rounds

    @property
    def c4(self) -> int:
        return self.__c4

    @c4.setter
    def c4(self, c4: int) -> None:
        self.__c4 = c4

    @property
    def c5(self) -> int:
        return self.__c5

    @c5.setter
    def c5(self, c5: int) -> None:
        self.__c5 = c5

    @property
    def penalty(self) -> int:
        return self.__penalty

    @penalty.setter
    def penalty(self, penalty: int) -> None:
        self.__penalty = penalty

    @property
    def solution(self) -> ndarray:
        return self.__solution

    @solution.setter
    def solution(self, solution: ndarray) -> None:
        self.__solution = solution

    @property
    def backtracked(self) -> list:
        return self.__backtracked

    @backtracked.setter
    def backtracked(self, backtracked: list) -> None:
        self.__backtracked = backtracked

    @staticmethod
    def __build_schedule(opp: ndarray) -> (ndarray, dict):
        rounds, teams = opp.shape
        games = teams // 2
        schedule_shape = rounds, games

        team_indexes = tile(arange(teams), (rounds, 1))
        home_games = (team_indexes[where(opp > 0)] + 1).reshape(schedule_shape)
        out_games = opp[opp > 0].reshape(schedule_shape)

        schedule = zeros((rounds, games, 2), dtype=int32)
        schedule[:, :, 0] = home_games
        schedule[:, :, 1] = out_games

        home_games_dict = {}
        team_numbers = unique(schedule.flatten())
        for team in team_numbers:
            home_games_dict[team] = where(home_games == team_numbers[team - 1])

        return schedule, home_games_dict

    @staticmethod
    def init_solution(rounds: int, umps: int) -> ndarray:
        solution = zeros((rounds, umps), dtype=int32)

        ump_indexes = arange(umps)
        for s in range(rounds):
            solution[s, :] = choice(ump_indexes, size=umps, replace=False) + 1

        return solution

    def print_solution(self) -> None:
        game_numbers = unique(self.solution)
        games = self.umps
        solution = zeros(self.solution.shape, dtype=int32)
        game_matrix = tile(game_numbers.reshape(1, games), (self.rounds, 1))

        for game in game_numbers:
            solution[:, game - 1] = game_matrix[where(self.solution == game)]

        print_solution(','.join(map(str, solution.flatten())), self.name)

    def __venues_of_umps(self, solution: ndarray, home=True) -> ndarray:
        games = self.schedule[:, :, 0 if home else 1]
        rounds, umps = solution.shape
        rows = tile(arange(rounds).reshape((rounds, 1)), (1, umps))

        return games[rows, solution - 1]

    def umps_distances(self, solution: ndarray, curr_round: int) -> ndarray:
        venues = self.__venues_of_umps(solution)
        distances = zeros(venues.shape, dtype=int32)

        for r in range(1, curr_round + 1):
            distances[r, :] = self.dist[venues[r - 1, :] - 1, venues[r, :] - 1]

        return distances

    @staticmethod
    def solutions_cross_product(s1: ndarray, s2: ndarray) -> ndarray:
        rounds, umps = s1.shape
        product = zeros((rounds + s2.shape[0], umps * umps), dtype=int32)

        for x in range(umps):
            for y in range(umps):
                col = x * umps + y
                product[:rounds, col] = s1[:, x]
                product[rounds:, col] = s2[:, y]

        return product

    def constraint3(self, solution: ndarray, curr_round: int) -> ndarray:
        """ Every umpire sees every team at least once at team's home. """

        venues = self.__venues_of_umps(solution)
        constraint = zeros(venues.shape, dtype=int32)

        venue_numbers = arange(1, self.teams + 1)
        for venue in range(venues.shape[1]):
            unvisit_venues = \
                set(venue_numbers) - set(unique(venues[:curr_round + 1, venue]))
            for _ in unvisit_venues:
                constraint[-1, venue] += self.penalty

        return constraint

    def constraint4(self, solution: ndarray, curr_round: int) -> ndarray:
        """
            No umpire is in the same site more than once in any `self.c4`
            consecutive slots.
        """

        constraint = zeros(solution.shape, dtype=int32)

        if self.c4 > 1:
            venues = self.__venues_of_umps(solution)
            rolled = venues

            for c in range(1, self.c4):
                rolled = roll(rolled, 1, axis=0)
                rolled[:c, :] = -1
                constraint += (venues == rolled).astype(int)

            constraint[curr_round + 1:, :] = 0

        constraint *= self.penalty * self.PENALTY

        return constraint

    def constraint5(self, solution: ndarray, curr_round: int) -> ndarray:
        """
            No umpire sees a team more than once in any `self.c5` consecutive
            slots.
        """

        constraint = zeros(solution.shape, dtype=int32)

        if self.c5 > 1:
            venues = self.__venues_of_umps(solution)
            rolled = venues
            out_venues = self.__venues_of_umps(solution, home=False)
            out_rolled = out_venues

            for _ in range(1, self.c5):
                rolled = roll(rolled, 1, axis=0)
                rolled[0, :] = -1
                out_rolled = roll(out_rolled, 1, axis=1)
                out_rolled[0, :] = -1
                constraint += \
                    (venues == rolled).astype(int) \
                    + (venues == out_rolled).astype(int) \
                    + (out_venues == rolled).astype(int) \
                    + (out_venues == out_rolled).astype(int)

            constraint[curr_round + 1:, :] = 0

        constraint *= self.penalty * self.PENALTY

        return constraint
