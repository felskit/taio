import sys

from src.classes.data import SchedulingData


class ParseError(Exception):
    """Exception type thrown when the input file is of invalid format."""
    pass


class Parser:
    """Class used to read and parse input files provided to the program."""
    line_no = 0

    def _parse_comma_delimited_numbers(self, file, arg_count):
        """
        Reads a line, containing comma-delimited numbers, from a file and parses it into a list.

        :param file: A file object to read the line from.
        :type file: io.TextIOWrapper
        :param arg_count: Expected number of comma-delimited numbers in the next line.
        :type arg_count: int
        :return: A list containing the numbers in the line read from the file.
        :rtype: list
        :raise ParseError: A :class:`ParseError` is thrown when:

            - The line read is empty, or the file has ended.
            - Some numbers are missing in the line (there is only whitespace between a pair of commas).
            - The number of numbers in the line does not match the *arg_count* argument.
            - One of the values in the line is not a base-10 integer.
        """
        self.line_no += 1
        line = file.readline()
        if len(line) == 0:
            raise ParseError('Line {}: Unexpected empty line or end-of-file hit'.format(self.line_no))
        stripped = [x.strip() for x in line.split(',')]
        if not all(stripped):
            raise ParseError('Line {}: At least one argument is missing a value.'.format(self.line_no))
        if len(stripped) != arg_count:
            raise ParseError('Line {}: {} arguments expected, got {}.'.format(self.line_no, arg_count, len(stripped)))
        try:
            vector = [int(s) for s in stripped]
        except ValueError:
            raise ParseError('Line {}: Non-base 10 integral value found'.format(self.line_no))
        return vector

    def _parse_counts(self, file):
        """
        Reads the counts of skills, experts and projects from the supplied file.

        :param file: A file object to read the line containing the counts from.
        :type file: io.TextIOWrapper
        :return: An instance of :class:`ProblemData` storing the counts of skills, experts and projects.
        :rtype: ProblemData
        :raise ParseError: A :class:`ParseError` is thrown when:

            - The number of skills is zero or lower.
            - The number of experts or projects is negative.
        """
        counts = self._parse_comma_delimited_numbers(file, 4)
        errors = []
        if counts[0] < 1:
            errors.append('The number of skills must be positive.')
        if counts[1] < 0:
            errors.append('The number of experts must be non-negative.')
        if counts[2] < 0:
            errors.append('The number of projects must be non-negative.')
        if counts[3] < 1:
            errors.append('The number of overall time units must be positive.')
        if len(errors) > 0:
            raise ParseError('\n'.join(errors))
        return SchedulingData(counts)

    def _parse_expert(self, file, skill_count):
        """
        Reads a single expert's skill vector from a file into a list.

        :param file: A file object to read the skill vector from.
        :type file: io.TextIOWrapper
        :param skill_count: The length of the skill vector, equal to the number of skills in the problem.
        :type skill_count: int
        :return: A list with binary values, containing information about the skills of an expert.
        :rtype: list
        :raise ParseError: A :class:`ParseError` is thrown when the contents of the vector read from file
        are non-binary.
        """
        vector = self._parse_comma_delimited_numbers(file, skill_count)
        if any([(x < 0 or x > 1) for x in vector]):
            raise ParseError('Line {}: Expert vectors must be binary'.format(self.line_no))
        return vector

    def _parse_experts(self, file, data):
        """
        Reads all experts' skill vectors from a file into a :class:`ProblemData` object.

        :param file: A file object to read the skill vectors from.
        :type file: io.TextIOWrapper
        :param data: A :class:`ProblemData` object to add the skill vectors to.
        :type data: ProblemData
        """
        for i in range(data.expert_count):
            vector = self._parse_expert(file, data.skill_count)
            data.add_expert(vector)

    def _parse_project(self, file, skill_count):
        """
        Reads a single project's requirements from a file into a list.

        :param file: A file object to read the requirements vector from.
        :type file: io.TextIOWrapper
        :param skill_count: The length of the requirements vector, equal to the number of skills in the problem.
        :type skill_count: int
        :return: A list with non-negative values, containing information about the requirements of a project.
        :rtype: list
        :raise ParseError: A :class:`ParseError` is thrown when the vector read from file contains negative values.
        """
        vector = self._parse_comma_delimited_numbers(file, skill_count + 1)
        if any([x < 0 for x in vector[:-1]]):
            raise ParseError('Line {}: Project requirement vector must be non-negative'.format(self.line_no))
        if vector[-1] < 1:
            raise ParseError('Line {}: The number of project time units must be positive'.format(self.line_no))
        return vector

    def _parse_projects(self, file, data):
        """
        Reads all projects' requirement vectors from a file into a :class:`SchedulingData` object.

        :param file: A file object to read the requirement vectors from.
        :type file: io.TextIOWrapper
        :param data: A :class:`ProblemData` object to add the requirement vectors to.
        :type data: ProblemData
        """
        for i in range(data.project_count):
            vector = self._parse_project(file, data.skill_count)
            data.add_project((vector[:-1], vector[-1]))

    def parse(self, file):
        """
        Parses the contents of an input file for a problem into a :class:`ProblemData` object.

        :param file: An opened file object to parse.
        :type file: io.TextIOWrapper
        :return: A :class:`ProblemData` object with problem instance info.
        :rtype: ProblemData
        """
        data = self._parse_counts(file)
        self._parse_experts(file, data)
        self._parse_projects(file, data)
        if len(file.readline()) > 0:
            sys.stderr.write('Data past line {} will be ignored\n'.format(self.line_no))
        return data
