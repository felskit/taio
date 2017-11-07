from src.classes.data import ProblemResult
from src.classes.graph import Graph


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
        max_flow_value, flow_graph = self.graph.maximum_flow(self.s, self.t)
        skills = dict((skill_id, []) for skill_id in range(self.skills_count))
        assignment = []

        for (expert_id, expert_skills) in enumerate(self.experts):
            for (skill_id, has_skill) in enumerate(expert_skills):
                if has_skill > 0:
                    if flow_graph.get_flow_value(self._v_expert(expert_id), self._v_skill(skill_id)) == 1:
                        skills[skill_id].append(expert_id)
                        break

        for (project_id, requirements) in enumerate(self.projects):
            for (skill_id, need) in enumerate(requirements):
                if need > 0:
                    flow_value = flow_graph.get_flow_value(self._v_skill(skill_id), self._v_project(project_id))
                    while flow_value > 0:
                        expert_id = skills[skill_id].pop()
                        assignment.append((expert_id, skill_id, project_id))
                        flow_value -= 1

        shortage = self.calculate_shortage(max_flow_value)
        return ProblemResult(shortage, assignment)

    def calculate_shortage(self, supply):
        demand = sum(sum(x) for x in self.projects)
        return demand - supply

    def _build_graph(self):
        self.graph = Graph()
        self._add_nodes()
        self._connect_experts_to_source()
        self._connect_experts_to_skills()
        self._connect_skills_to_projects()
        self._connect_projects_to_sink()

    def _add_nodes(self):
        self.graph.add_nodes(list(range(self.t + 1)))

        # self.graph.add_nodes([self.s, self.t])
        # for expert_id in range(self.expert_count):
        #     self.graph.add_node(self._v_expert(expert_id))
        # for skill_id in range(self.skills_count):
        #     self.graph.add_node(self._v_skill(skill_id))
        # for project_id in range(self.project_count):
        #     self.graph.add_node(self._v_project(project_id))

    def _connect_experts_to_source(self):
        for expert_id in range(self.expert_count):
            self.graph.add_edge(self.s, self._v_expert(expert_id), capacity=1)

    def _connect_experts_to_skills(self):
        for (expert_id, expert_skills) in enumerate(self.experts):
            for (skill_id, has_skill) in enumerate(expert_skills):
                if has_skill > 0:
                    self.graph.add_edge(self._v_expert(expert_id), self._v_skill(skill_id), capacity=has_skill)

    def _connect_skills_to_projects(self):
        for (project_id, requirements) in enumerate(self.projects):
            for (skill_id, need) in enumerate(requirements):
                if need > 0:
                    self.graph.add_edge(self._v_skill(skill_id), self._v_project(project_id), capacity=need)

    def _connect_projects_to_sink(self):
        for (project_id, requirements) in enumerate(self.projects):
            c = sum(requirements)
            if c > 0:
                self.graph.add_edge(self._v_project(project_id), self.t, capacity=c)

    def _v_expert(self, expert_id):
        return expert_id + 1

    def _v_skill(self, skill_id):
        return skill_id + self.expert_count + 1

    def _v_project(self, project_id):
        return project_id + self.skills_count + self.expert_count + 1
