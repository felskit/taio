import unittest
import random
import time

from src.classes.data import ProblemData
from src.utils.solver import Solver


class SolverTest(unittest.TestCase):
    @staticmethod
    def _setup_input(counts, experts, projects):
        input_data = ProblemData(counts)
        input_data.experts = experts
        input_data.projects = projects
        return input_data

    def assertCorrect(self, assignment, projects):
        expert_set = set()
        assignments = [[0] * len(project) for project in projects]
        for expert, skill, project in assignment:
            if expert in expert_set:
                raise self.failureException('Expert {} was assigned to two subtasks'.format(expert))
            else:
                expert_set.add(expert)
            assignments[project][skill] += 1
            if assignments[project][skill] > projects[project][skill]:
                raise self.failureException('Overassigned project {} in skill {}\n'
                                            'Project assignment: {}\n'
                                            'Project requirements: {}'
                                            .format(project, skill, assignments[project], projects[project]))

    def test_basic_graph(self):
        """Input data specifies basic graph with unequivocal assignment."""
        # given
        experts = [[1, 0], [1, 0], [0, 0]]
        projects = [[2, 1], [1, 2]]
        input_data = self._setup_input([2, len(experts), len(projects)], experts, projects)
        # when
        result = Solver(input_data).solve()
        # then
        self.assertEqual(result.shortage, 4)
        self.assertEqual(result.assignment, [(1, 0, 0), (0, 0, 0)])
        self.assertCorrect(result.assignment, projects)

    def test_no_experts(self):
        """Input data specifies no experts."""
        # given
        experts = []
        projects = [[3, 2, 1], [1, 2, 3]]
        input_data = self._setup_input([3, len(experts), len(projects)], experts, projects)
        # when
        result = Solver(input_data).solve()
        # then
        self.assertEqual(result.shortage, 12)
        self.assertEqual(len(result.assignment), 0)
        self.assertCorrect(result.assignment, projects)

    def test_no_projects(self):
        """Input data specifies no projects."""
        # given
        experts = [[1] * 3] * 2
        projects = []
        input_data = self._setup_input([3, len(experts), len(projects)], experts, projects)
        # when
        result = Solver(input_data).solve()
        # then
        self.assertEqual(result.shortage, 0)
        self.assertEqual(len(result.assignment), 0)
        self.assertCorrect(result.assignment, projects)

    def test_experts_zeroes_only(self):
        """Expert vectors only contain zeroes."""
        experts = [[0] * 4] * 3
        projects = [[1] * 4, [2] * 4, [3] * 4]
        input_data = self._setup_input([4, len(experts), len(projects)], experts, projects)
        # when
        result = Solver(input_data).solve()
        # then
        self.assertEqual(result.shortage, 24)
        self.assertEqual(len(result.assignment), 0)
        self.assertCorrect(result.assignment, projects)

    def test_project_zeroes_only(self):
        """Project vectors only contain zeroes."""
        # given
        experts = [[1] * 3] * 2
        projects = [[0] * 3] * 2
        input_data = self._setup_input([3, len(experts), len(projects)], experts, projects)
        # when
        result = Solver(input_data).solve()
        # then
        self.assertEqual(result.shortage, 0)
        self.assertEqual(len(result.assignment), 0)
        self.assertCorrect(result.assignment, projects)

    def test_ideal_assignment(self):
        """Every expert can be assigned a subtask. All projects are completed with no shortages."""
        experts = [[1] * 5] * 20
        projects = [[1] * 5, [3] * 5]
        input_data = self._setup_input([5, len(experts), len(projects)], experts, projects)
        # when
        result = Solver(input_data).solve()
        # then
        self.assertEqual(result.shortage, 0)
        self.assertEqual(len(result.assignment), 20)
        self.assertCorrect(result.assignment, projects)

    def test_project_bottleneck(self):
        """Project requirements are the bottleneck - there are more experts able to do the work than subtasks."""
        # given
        experts = [[1] * 3] * 3
        projects = [[1, 0, 0]] * 2
        input_data = self._setup_input([3, len(experts), len(projects)], experts, projects)
        # when
        result = Solver(input_data).solve()
        # then
        self.assertEqual(result.shortage, 0)
        self.assertEqual(len(result.assignment), 2)
        self.assertCorrect(result.assignment, projects)

    def test_expert_bottleneck(self):
        """Expert supply is the bottleneck - there are more subtasks to do than available experts."""
        # given
        experts = [[1, 0, 1, 0]] * 3 + [[0, 1, 0, 1]] * 5 + [[0, 1, 1, 0]] * 2
        projects = [[1, 1, 1, 1]] * 7
        input_data = self._setup_input([4, len(experts), len(projects)], experts, projects)
        # when
        result = Solver(input_data).solve()
        # then
        self.assertEqual(result.shortage, 18)
        self.assertEqual(len(result.assignment), 10)
        self.assertCorrect(result.assignment, projects)

    def test_big_graph(self):
        """Tests the algorithm on a big input graph."""
        def rand_int_vect_of_size_n(maxval, n):
            return [random.randint(0, maxval) for _ in range(n)]

        projects_count = 100 * 2
        experts_count = 100 * 2
        skills_count = 100 * 2
        experts = [rand_int_vect_of_size_n(1, skills_count) for _ in range(experts_count)]
        projects = [rand_int_vect_of_size_n(skills_count, skills_count) for _ in range(projects_count)]

        solver = Solver(self._setup_input([projects_count, experts_count, projects_count], experts, projects))
        # self.time_me(solver, "3 x 1000 test")

    @staticmethod
    def time_me(solver, name):
        start = time.time()
        solver.solve()
        print("{} took {} s".format(name, time.time() - start))