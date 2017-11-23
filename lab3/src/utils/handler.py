import random
from src.classes.data import ProblemData
from src.utils.solver import Solver


class GeneticHandler:
    def __init__(self, scheduling_data, population_count):
        self.scheduling_data = scheduling_data
        self.population_count = population_count
        self.population = [
            [random.randint(0, scheduling_data.overall_time_units - 1) for _ in range(scheduling_data.project_count)]
            for _ in range(population_count)]

    def _validate_scheduling(self, member):  # check if scheduling even makes sense
        for i, p_from in enumerate(member):
            p_length = self.scheduling_data.projects[i][1]
            if p_from + p_length > self.scheduling_data.overall_time_units:
                return False
        return True

    def _find_intervals(self, member):
        if len(member) == 0:  # no projects specified
            return []

        events = []
        projects = []
        for i, p_from in enumerate(member):
            p_to = p_from + self.scheduling_data.projects[i][1]
            events.extend((p_from, p_to))
            projects.append((i, p_from, p_to))  # index i added in case of sweeping
        events = list(set(events))
        events.sort()

        # might be useful for sweeping
        # import functools
        #
        # def compare(a, b):
        #     return a[1] - b[1]
        #
        # projects = sorted(projects, key=functools.cmp_to_key(compare))

        intervals = []
        for i_from, i_to in zip(events[:-1], events[2:]):
            i_projects = []
            for i, p_from, p_to in projects:
                if p_from >= i_from and p_to <= i_to:
                    i_projects.append(i)
            intervals.append((i_from, i_to, i_projects))

        return intervals

    def _interval_to_problem_data(self, interval):
        counts = [self.scheduling_data.skill_count,
                  self.scheduling_data.expert_count,
                  self.scheduling_data.project_count]  # maybe have this added from the start
        data = ProblemData(counts)

        for expert in self.scheduling_data.experts:
            data.add_expert(expert)

        for i in interval[2]:
            project, _ = self.scheduling_data.projects[i]  # _ is project length
            data.add_project(project)

        return data

    def _solve_scheduling(self, member):
        if not self._validate_scheduling(member):
            return -1  # return -1 because scheduling doesn't make sense (means it has to be removed from population)

        total_shortage = 0
        assignments = []  # store these so that we don't have to solve again if this turns out to be the best solution?

        intervals = self._find_intervals(member)
        for interval in intervals:
            problem_data = self._interval_to_problem_data(interval)
            problem_result = Solver(problem_data).solve()

            i_length = interval[1] - interval[0]
            total_shortage += problem_result.shortage * i_length  # problem_result.shortage is in one time unit
            assignments.append(problem_result.assignment)

        return total_shortage, assignments, intervals  # intervals may be useful for constructing final assignment? idk

    def solve(self):
        return "Solved."
