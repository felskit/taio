import unittest

from src.classes.data import ProblemData
from src.utils.solver import Solver


class SolverTest(unittest.TestCase):
    def test_basic_graph(self):
        input_data = self._setup_input([2, 3, 2], [[1, 0], [1, 0], [0, 0]], [[2, 1], [1, 2]])
        expected = [(1, 0, 0), (0, 0, 0)]

        result = Solver(input_data).solve()

        self.assertEqual(result.expert_to_skill, expected)

    def _setup_input(self, counts, experts, projects):
        input_data = ProblemData(counts)
        input_data.experts = experts
        input_data.projects = projects
        return input_data
