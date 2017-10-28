class ProblemData:
    experts = []
    projects = []

    def __init__(self, counts):
        assert len(counts) == 3
        self.skill_count = counts[0]
        self.expert_count = counts[1]
        self.project_count = counts[2]

    def add_expert(self, vector):
        self.experts.append(vector)

    def add_project(self, vector):
        self.projects.append(vector)
