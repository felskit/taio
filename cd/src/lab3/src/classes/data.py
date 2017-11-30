class ProblemData:
    """
    Stores all required data associated with a problem instance:

        - the counts of skills, experts and projects,
        - binary skill vectors of experts,
        - non-negative requirement vectors of projects.
    """

    def __init__(self, counts):
        """
        Initializes the instance.

        :param counts: A list of skill, expert and project counts.

            - The list **must be** of length 3.
            - The first element of the list should be the skill count.
            - The second element of the list should be the expert count.
            - The third element of the list should be the project count.
        :type counts: list
        """
        assert len(counts) == 3
        self.skill_count = counts[0]
        self.expert_count = counts[1]
        self.project_count = counts[2]
        self.projects = []
        self.experts = []

    def add_expert(self, vector):
        """
        Adds a skill vector for an expert to the list of expert vectors.

        :param vector: A skill vector to be added to the data.
        :type vector: list
        """
        self.experts.append(vector)

    def add_project(self, vector):
        """
        Adds a requirement vector for a project to the list of project vectors.

        :param vector: A requirement vector to be added to the data.
        :type vector: list
        """
        self.projects.append(vector)


class ProblemResult:
    """Contains information about the solution for the supplied problem instance."""

    def __init__(self, shortage, assignment):
        """
        Constructor.

        :param shortage: The expert shortage in the assignment found.
        :type shortage: int
        :param assignment: The expert assignment.
                           This is a list containing tuples with three elements:

                           1. the expert number,
                           2. the number of the skill the expert will be using,
                           3. the number of the project the expert will be using the skill in.
        :type assignment: list
        """
        self.shortage = shortage
        self.assignment = assignment

    def __str__(self):
        """
        Returns the string representation of the result.

        :return: String to be printed to the user as an output.
        :rtype: str
        """
        return 'Shortage: {}\nAssignment: {}'.format(str(self.shortage), str(self.assignment))


class SchedulingData:
    experts = []
    projects = []

    def __init__(self, counts):
        assert len(counts) == 4
        self.skill_count = counts[0]
        self.expert_count = counts[1]
        self.project_count = counts[2]
        self.overall_time_units = counts[3]

    def add_expert(self, expert_vector):
        self.experts.append(expert_vector)

    def add_project(self, project_tuple):
        self.projects.append(project_tuple)
