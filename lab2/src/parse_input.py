import sys

from .data import ProblemData


class ParseError(Exception):
    pass


class Parser:
    line_no = 0

    def parse_comma_delimited_numbers(self, file, arg_count):
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

    def parse_counts(self, file):
        counts = self.parse_comma_delimited_numbers(file, 3)
        errors = []
        if counts[0] < 1:
            errors.append('The number of skills must be positive.')
        if counts[1] < 0:
            errors.append('The number of experts must be non-negative.')
        if counts[2] < 0:
            errors.append('The number of projects must be non-negative.')
        if len(errors) > 0:
            raise ParseError('\n'.join(errors))
        return ProblemData(counts)

    def parse_expert(self, file, skill_count):
        vector = self.parse_comma_delimited_numbers(file, skill_count)
        if any([(x < 0 or x > 1) for x in vector]):
            raise ParseError('Line {}: Expert vectors must be binary'.format(self.line_no))
        return vector

    def parse_experts(self, file, data):
        for i in range(data.expert_count):
            vector = self.parse_expert(file, data.skill_count)
            data.add_expert(vector)

    def parse_project(self, file, skill_count):
        vector = self.parse_comma_delimited_numbers(file, skill_count)
        if any([x < 0 for x in vector]):
            raise ParseError('Line {}: Project vectors must be non-negative'.format(self.line_no))
        return vector

    def parse_projects(self, file, data):
        for i in range(data.project_count):
            vector = self.parse_project(file, data.skill_count)
            data.add_project(vector)

    def parse(self, file):
        data = self.parse_counts(file)
        self.parse_experts(file, data)
        self.parse_projects(file, data)
        if len(file.readline()) > 0:
            sys.stderr.write('Data past line {} will be ignored\n'.format(self.line_no))
        return data
