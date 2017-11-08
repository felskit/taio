from src.classes.data import ProblemResult
from src.classes.graph import Graph


class Solver:
    def __init__(self, input_data):
        """
        Initializes the solver using the supplied input data.

        :param input_data: An instance of :class:`src.classes.data.ProblemData` containing information
                           about the problem instance.
        :type input_data: src.classes.data.ProblemData
        """
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
        """
        Solves the problem for the data supplied via constructor.

        :return: A :class:`ProblemResult` object containing the solution, consisting of the expert shortage as a number
                 and an assignment of experts to projects.
        :rtype: ProblemResult
        """
        # Find maximum flow in the graph.
        max_flow_value, flow_graph = self.graph.maximum_flow(self.s, self.t)
        skills = dict((skill_id, []) for skill_id in range(self.skills_count))
        assignment = []

        # Split the experts into the skills they were chosen to by the maximum flow.
        for (expert_id, expert_skills) in enumerate(self.experts):
            for (skill_id, has_skill) in enumerate(expert_skills):
                if has_skill > 0:
                    if flow_graph.get_flow_value(self._v_expert(expert_id), self._v_skill(skill_id)) == 1:
                        skills[skill_id].append(expert_id)
                        break

        # Given the list of experts assigned to skills, assign them project-by-project according to their needs.
        # This can be done naively; Kirchhoff's law for networks ensures that incoming and outgoing flow for skill
        # vertices will be equal.
        for (project_id, requirements) in enumerate(self.projects):
            for (skill_id, need) in enumerate(requirements):
                if need > 0:
                    flow_value = flow_graph.get_flow_value(self._v_skill(skill_id), self._v_project(project_id))
                    while flow_value > 0:
                        expert_id = skills[skill_id].pop()
                        assignment.append((expert_id, skill_id, project_id))
                        flow_value -= 1

        shortage = self._calculate_shortage(max_flow_value)
        return ProblemResult(shortage, assignment)

    def _calculate_shortage(self, supply):
        """
        Calculates the expert shortage for the problem solution.

        :param supply: Expert supply, equivalent to the maximum flow in the constructed graph.
        :type supply: int
        :return: The expert shortage as a number.
        :rtype: int
        """
        demand = sum(sum(x) for x in self.projects)
        return demand - supply

    def _build_graph(self):
        """Builds the network graph corresponding to the problem instance being solved."""
        self.graph = Graph()
        self._add_nodes()
        self._connect_experts_to_source()
        self._connect_experts_to_skills()
        self._connect_skills_to_projects()
        self._connect_projects_to_sink()

    def _add_nodes(self):
        """Adds nodes for experts, skills and projects, as well as the network source and sink, to the graph."""
        self.graph.add_nodes(list(range(self.t + 1)))

    def _connect_experts_to_source(self):
        """Connects all expert nodes to the network source with an edge of capacity 1."""
        for expert_id in range(self.expert_count):
            self.graph.add_edge(self.s, self._v_expert(expert_id), capacity=1)

    def _connect_experts_to_skills(self):
        """
        Connects all expert nodes to the skills they possess, with an edge of capacity 1.
        If an expert *e* doesn't possess the skill *u*, no edge is added.
        """
        for (expert_id, expert_skills) in enumerate(self.experts):
            for (skill_id, has_skill) in enumerate(expert_skills):
                if has_skill > 0:
                    self.graph.add_edge(self._v_expert(expert_id), self._v_skill(skill_id), capacity=has_skill)

    def _connect_skills_to_projects(self):
        """
        Connects skill nodes to the projects that require experts qualified in that particular skill.

        The capacity of the edges is equal to the number of experts needed in the projects.
        If a project *p* doesn't need experts qualified in skill *u*, no edge is added.
        """
        for (project_id, requirements) in enumerate(self.projects):
            for (skill_id, need) in enumerate(requirements):
                if need > 0:
                    self.graph.add_edge(self._v_skill(skill_id), self._v_project(project_id), capacity=need)

    def _connect_projects_to_sink(self):
        """
        Connects project nodes to the network sink with an edge of capacity equal to the sum of the project requirement
        vector.
        This ensures that the capacity of that particular edge is not a bottleneck when calculating the maximum flow.
        """
        for (project_id, requirements) in enumerate(self.projects):
            c = sum(requirements)
            if c > 0:
                self.graph.add_edge(self._v_project(project_id), self.t, capacity=c)

    @staticmethod
    def _v_expert(expert_id):
        """
        Gets the number of the vertex corresponding to an expert with the supplied ID in the graph.

        :param expert_id: The ID number of the expert.
        :type expert_id: int
        :return: The number of the vertex corresponding to the expert.
        :rtype: int
        """
        return expert_id + 1

    def _v_skill(self, skill_id):
        """
        Gets the number of the vertex corresponding to a skill with the supplied ID in the graph.

        :param skill_id: The ID number of the skill.
        :type skill_id: int
        :return: The number of the vertex corresponding to the skill.
        :rtype: int
        """
        return skill_id + self.expert_count + 1

    def _v_project(self, project_id):
        """
        Gets the number of the vertex corresponding to a project with the supplied ID in the graph.

        :param project_id: The ID number of the project.
        :type project_id: int
        :return: The number of the vertex corresponding to the project.
        :rtype: int
        """
        return project_id + self.skills_count + self.expert_count + 1
