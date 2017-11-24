import random
from collections import OrderedDict

from src.classes.data import ProblemData
from src.utils.solver import Solver


class GeneticSolver:
    def __init__(self, scheduling_data):
        self.scheduling_data = scheduling_data
        self.population_count = 500
        self.max_generation_count = 100
        self.crossover_chance = 0.4
        self.mutation_chance = 0.05
        self.max_iterations_without_change = 5
        self.population = self._init_population()
        self.counts = [
            scheduling_data.skill_count,
            scheduling_data.expert_count,
            scheduling_data.project_count
        ]

    def _init_population(self):
        population = OrderedDict()
        for _ in range(self.population_count):
            member = []
            for i in range(self.scheduling_data.project_count):
                p_length = self.scheduling_data.projects[i][1]
                member.append(random.randint(0, max(1, self.scheduling_data.overall_time_units - p_length)))
            population[tuple(member)] = None
        return population

    # checks if scheduling even makes sense
    def _validate_scheduling(self, member):
        for i, p_from in enumerate(member):
            p_length = self.scheduling_data.projects[i][1]
            if p_from + p_length > self.scheduling_data.overall_time_units:
                return False
        return True

    # finds intervals
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
            if len(i_projects) > 0:  # don't even consider intervals w/o projects
                intervals.append((i_from, i_to, i_projects))

        return intervals

    def _interval_to_problem_data(self, interval):
        data = ProblemData(self.counts)

        for expert in self.scheduling_data.experts:
            data.add_expert(expert)

        for i, project in enumerate(self.scheduling_data.projects):
            if i in interval[2]:
                data.add_project(project[0])
            else:
                data.add_project([0] * self.scheduling_data.skill_count)

        return data

    # fitness function
    def _solve_scheduling(self, member):
        if not self._validate_scheduling(member):
            return -1, None, None  # scheduling doesn't make sense

        total_shortage = 0
        assignments = []

        intervals = self._find_intervals(member)
        for interval in intervals:
            problem_data = self._interval_to_problem_data(interval)
            problem_result = Solver(problem_data).solve()

            i_length = interval[1] - interval[0]
            total_shortage += problem_result.shortage * i_length  # problem_result.shortage is in one time unit
            assignments.append(problem_result.assignment)

        return total_shortage, assignments, intervals

    def _n_point_crossover(self, parent1, parent2, n):
        offspring1 = list(parent1)
        offspring2 = list(parent2)

        # parents are empty (no projects) or they have only one gene, so no point in doing crossover
        if self.scheduling_data.project_count == 0 or self.scheduling_data.project_count == 1:
            return tuple(offspring1), tuple(offspring2)

        cuts = random.sample(range(1, self.scheduling_data.project_count), n)
        cuts.sort()
        cuts.append(self.scheduling_data.project_count)

        for cut_from, cut_to in zip(cuts[::2], cuts[1::2]):
            offspring1[cut_from:cut_to] = parent2[cut_from:cut_to]
            offspring2[cut_from:cut_to] = parent1[cut_from:cut_to]

        return tuple(offspring1), tuple(offspring2)

    def _n_point_mutation(self, member, n):
        mutated = list(member)

        # member is empty (no projects) or there's no way to mutate since only one gene is allowed (0)
        if self.scheduling_data.project_count <= 1:
            return tuple(mutated)

        mutation = random.sample(range(0, self.scheduling_data.project_count), n)
        possible_genes = list(range(0, self.scheduling_data.overall_time_units))

        for i in mutation:
            original_gene = member[i]
            possible_genes.remove(original_gene)
            mutated[i] = random.sample(possible_genes, 1)[0]
            possible_genes.append(original_gene)

        return tuple(mutated)

    def solve(self):
        generation_counter = 1
        best_member = None
        best_solution = None
        last_change_in_best = 0

        while True:
            # Generation evaluation.
            current_best_member = None
            current_best_solution = None

            print('Evaluating generation #{} ({} members)... '
                  .format(generation_counter, len(self.population)), end='', flush=True)
            for member, solution in self.population.items():
                if not solution:
                    self.population[member] = self._solve_scheduling(member)
                if not current_best_solution or current_best_solution[0] < 0 \
                        or current_best_solution[0] > self.population[member][0] >= 0:
                    current_best_member = member
                    current_best_solution = self.population[member]
            print('Finished.')

            # Updating all-time best result
            if not best_solution or best_solution[0] < 0 or \
                    current_best_solution and best_solution[0] > current_best_solution[0] > 0:
                best_member = current_best_member
                best_solution = current_best_solution
                last_change_in_best = 0
            else:
                last_change_in_best += 1

            # Stop conditions.
            if best_solution and best_solution[0] == 0:
                print('Found optimal solution. Finishing algorithm.')
                return best_member, best_solution

            if best_member and last_change_in_best >= self.max_iterations_without_change:
                print('Best result has not changed since {} iterations. Finishing algorithm.'
                      .format(self.max_iterations_without_change))
                return best_member, best_solution

            if generation_counter > self.max_generation_count:
                print('Reached generation limit. Finishing algorithm.')
                return best_member, best_solution

            self.print_result(best_member, best_solution)

            # Population control.
            print('\nEvolving generation #{} into generation #{}.'.format(generation_counter, generation_counter + 1))
            invalid = []
            fitness_sum = 0

            print('> Validating population of {} members... '.format(len(self.population)), end='', flush=True)
            for member, solution in self.population.items():
                if solution[0] > 0:
                    fitness_sum += 1 / solution[0]
                else:
                    invalid.append(member)
            print('Finished.')

            if len(invalid) > 0:
                print('> Removing invalid members... ', end='', flush=True)
                for member in invalid:
                    del self.population[member]
                print('Finished.')
            print('> Valid members in population: {}.'.format(len(self.population)))

            if len(self.population) >= self.population_count:
                print('> Population too big. Selecting {} members from {}... '
                      .format(self.population_count, len(self.population)), end='', flush=True)
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
                print('Finished.')

            # Crossovers.
            crossover_members = random.sample(self.population.keys(), int(len(self.population) * self.crossover_chance))
            print('> Starting crossovers of {} members... '.format(len(crossover_members) // 2 * 2), end='', flush=True)
            for member1, member2 in zip(crossover_members[::2], crossover_members[1::2]):
                n = random.randint(1, self.scheduling_data.project_count - 1)
                offspring1, offspring2 = self._n_point_crossover(member1, member2, n)
                self.population[offspring1] = None
                self.population[offspring2] = None
            print('Finished.')

            # Mutations.
            mutation_members = random.sample(self.population.keys(), int(len(self.population) * self.mutation_chance))
            print('> Starting mutations of {} members... '.format(len(mutation_members)), end='', flush=True)
            for member in mutation_members:
                n = random.randint(1, self.scheduling_data.project_count - 1)
                mutated = self._n_point_mutation(member, n)
                self.population[mutated] = None
            print('Finished.\n')

            # Generation counter incrementation.
            generation_counter += 1

    @staticmethod
    def print_result(member, solution):
        print('Total shortage: {}.'.format(solution[0]))
        print('Best starting times for projects: {}.'.format(member))
        print('Intervals [t_from, t_to] -> [projects] with assignments (expert, skill, project):')
        for assignment, interval in zip(solution[1], solution[2]):
            print('[{},{}] -> {}: {}'.format(interval[0], interval[1], list(interval[2]), assignment))
