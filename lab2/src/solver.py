from .graph import Graph
from .data import ProblemResult


class Solver:
    def __init__(self, input_data):
        self.experts = input_data.experts
        self.projects = input_data.projects

        self.expert_count = input_data.expert_count
        self.project_count = input_data.project_count
        self.skills_count = input_data.skill_count

        nodes_count = self.expert_count + self.project_count + self.skills_count
        self.s = 0
        self.t = nodes_count + 1

        self._build_graph()

    def solve(self):
        _, flow_graph = self.graph.maximum_flow(self.s, self.t)

        result = []
        for expert_id in range(self.expert_count):
            skill = -1
            for skill_id in range(self.skills_count):
                if flow_graph.get_flow_value(self._v_expert(expert_id), self._v_skill(skill_id)) == 1:
                    skill = skill_id
            result.append(skill)

        return ProblemResult(result)

    def _build_graph(self):
        self.graph = Graph()
        self._add_experts_to_graph()
        self._add_experts_with_skills()
        self._assign_skills_to_projects()
        self._connect_projects_with_termination_vertex()

    def _add_experts_to_graph(self):
        for expert_id in range(self.expert_count):
            self.graph.add_edge(self.s, self._v_expert(expert_id), capacity=1)

    def _add_experts_with_skills(self):
        for (expert_id, skills) in enumerate(self.experts):
            for (skill_id, has_skill) in enumerate(skills):
                self.graph.add_edge(self._v_expert(expert_id), self._v_skill(skill_id), capacity=has_skill)

    def _assign_skills_to_projects(self):
        for (project_id, requirements) in enumerate(self.projects):
            for (skill_id, need) in enumerate(requirements):
                self.graph.add_edge(self._v_skill(skill_id), self._v_project(project_id), capacity=need)

    def _connect_projects_with_termination_vertex(self):
        for (project_id, requirements) in enumerate(self.projects):
            self.graph.add_edge(self._v_project(project_id), self.t, capacity=sum(requirements))

    def _v_expert(self, expert_id):
        return expert_id + 1

    def _v_skill(self, skill_id):
        return skill_id + self.expert_count + 1

    def _v_project(self, project_id):
        return project_id + self.skills_count + self.expert_count + 1

