import random
from collections import OrderedDict

from src.classes.data import ProblemData
from src.utils.solver import Solver


class GeneticHandler:
    def __init__(self, scheduling_data, population_count):
        self.scheduling_data = scheduling_data
        self.population_count = population_count
        self.generation_count = 100  # TODO: parameter?
        self.crossover_chance = 0.4  # TODO: parameter?
        self.mutation_chance = 0.05  # TODO: parameter?
        self.max_iterations_without_change = 10  # TODO: parameter?
        self.population = OrderedDict([
            (
                tuple(random.randint(0, scheduling_data.overall_time_units - 1) for _
                      in range(scheduling_data.project_count)),
                None
            )
            for _ in range(population_count)])

    def _validate_scheduling(self, member):  # check if scheduling even makes sense
        for i, p_from in enumerate(member):
            p_length = self.scheduling_data.projects[i][1]
            if p_from + p_length > self.scheduling_data.overall_time_units:
                return False
        return True

    def _find_intervals(self, member):
        if self.scheduling_data.project_count == 0:  # no projects specified
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
        for i_from, i_to in zip(events[:-1], events[1:]):
            i_projects = set()
            for i, p_from, p_to in projects:
                if i_from < p_to and p_from < i_to:
                    i_projects.add(i)
            intervals.append((i_from, i_to, i_projects))

        return intervals

    def _interval_to_problem_data(self, interval):
        counts = [self.scheduling_data.skill_count,
                  self.scheduling_data.expert_count,
                  self.scheduling_data.project_count]  # maybe have this added from the start
        data = ProblemData(counts)

        for expert in self.scheduling_data.experts:
            data.add_expert(expert)

        # for i in interval[2]:
        #     project, _ = self.scheduling_data.projects[i]  # _ is project length
        #     data.add_project(project)
        for i, project in enumerate(self.scheduling_data.projects):
            if i in interval[2]:
                data.add_project(project[0])
            else:
                data.add_project([0] * self.scheduling_data.skill_count)
        return data

    def _solve_scheduling(self, member):  # fitness function
        if not self._validate_scheduling(member):
            return -1, None, None  # return -1 because scheduling doesn't make sense

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

    def _n_point_crossover(self, parent1, parent2, n):
        offspring1 = list(parent1)
        offspring2 = list(parent2)

        # parents are empty (no projects) or they have only one gene, so no point in doing crossover
        if self.scheduling_data.project_count == 0 or self.scheduling_data.project_count == 1:
            return tuple(offspring1), tuple(offspring2)

        cuts = random.sample(range(1, self.scheduling_data.project_count), n)  # will throw ValueError if n too big
        cuts.sort()

        if n % 2 == 1:
            cuts.append(self.scheduling_data.project_count)

        for cut_from, cut_to in zip(cuts[::2], cuts[1::2]):
            offspring1[cut_from:cut_to] = parent2[cut_from:cut_to]
            offspring2[cut_from:cut_to] = parent1[cut_from:cut_to]

        return tuple(offspring1), tuple(offspring2)

    def _n_point_mutation(self, member, n):
        mutated = list(member)

        # member is empty (no projects) or no way to mutate since only one gene is allowed (0)
        if self.scheduling_data.project_count == 0 or self.scheduling_data.overall_time_units == 1:
            return tuple(mutated)

        mutation = random.sample(range(0, self.scheduling_data.project_count), n)  # will throw ValueError if n too big
        possible_genes = list(range(0, self.scheduling_data.overall_time_units))

        for i in mutation:
            original_gene = member[i]
            possible_genes.remove(original_gene)
            mutated[i] = random.sample(possible_genes, 1)[0]
            possible_genes.append(original_gene)

        return tuple(mutated)

    def solve(self):
        generation = 0
        best_solution = None
        best_member = None
        last_change_in_best = 0
        while True:
            # Evaluate generation.
            print('Evaluating')
            current_solution = None
            current_member = None
            for member, solution in self.population.items():
                if not solution:
                    self.population[member] = self._solve_scheduling(member)
                if not current_solution or current_solution[0] < 0 \
                        or current_solution[0] > self.population[member][0] >= 0:
                    current_member = member
                    current_solution = self.population[member]

            if best_solution is None or best_solution[0] < 0 or \
                    (current_solution is not None and best_solution[0] > current_solution[0] > 0):
                best_solution = current_solution
                best_member = current_member
                last_change_in_best = 0
            else:
                last_change_in_best += 1

            # Stop conditions.
            if last_change_in_best >= self.max_iterations_without_change and best_member is not None:
                return best_member, best_solution

            if best_solution and best_solution[0] == 0:
                return best_member, best_solution

            if generation >= self.generation_count:
                return best_member, best_solution

            print(best_solution)
            print(best_member)
            print('Starting generation {}'.format(generation))

            # Reduce the population.
            fitness_sum = 0
            invalid = []
            for member, solution in self.population.items():
                if solution[0] > 0:  # disregard -1s
                    fitness_sum += 1 / solution[0]
                else:
                    invalid.append(member)

            for member in invalid:
                del self.population[member]

            actual_count = len(self.population)
            print('Surviving count: {}'.format(actual_count))

            if actual_count >= self.population_count:
                self._reduce_population(fitness_sum)  # TODO: Too many can die
                print('Reducing population')

            print('After reduction: {}'.format(len(self.population)))
            actual_count = len(self.population)

            # Crossover.
            print('Crossover')
            crossover_members = random.sample(self.population.keys(), int(actual_count * self.crossover_chance))
            for first, second in zip(crossover_members[::2], crossover_members[1::2]):
                n = random.randint(1, self.scheduling_data.project_count - 1)
                first_offspring, second_offspring = self._n_point_crossover(first, second, n)
                self.population[first_offspring] = None
                self.population[second_offspring] = None

            # Mutation.
            print('Mutation')
            mutation_members = random.sample(self.population.keys(), int(actual_count * self.mutation_chance))
            for member in mutation_members:
                n = random.randint(1, self.scheduling_data.project_count - 1)
                mutated = self._n_point_mutation(member, n)
                self.population[mutated] = None

            # Increment counter.
            generation += 1

    def _reduce_population(self, fitness_sum):
        new_population = OrderedDict()
        for _ in range(self.population_count):
            chosen_member, chosen_solution = None, None
            random_value = random.uniform(0, fitness_sum)
            for member, solution in self.population.items():
                random_value -= 1 / solution[0]
                if random_value < 0:
                    chosen_member, chosen_solution = member, solution
                    break
            del self.population[chosen_member]
            fitness_sum -= chosen_solution[0]
            new_population[chosen_member] = chosen_solution
        self.population = new_population
