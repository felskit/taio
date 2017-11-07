import os
import shutil
import tempfile
import unittest

from src.utils.parser import Parser, ParseError


class ParserTest(unittest.TestCase):
    def setUp(self):
        self.test_directory = tempfile.mkdtemp()
        file_path = os.path.join(self.test_directory, 'test.txt')
        self.test_file = open(file_path, 'w+')
        self.parser = Parser()

    def _write_to_file(self, contents):
        self.test_file.write(contents)
        self.test_file.seek(0)

    def assertRaisesParseError(self, regex):
        self.assertRaisesRegex(
            ParseError,
            regex,
            self.parser.parse,
            self.test_file
        )

    def test_parse_empty_file(self):
        # when test file is empty expect
        self.assertRaisesParseError(r'Unexpected empty line')

    def test_parse_file_with_invalid_first_line(self):
        # given
        self._write_to_file('1,2,3,4')
        # expect
        self.assertRaisesParseError(r'3 arguments expected, got 4')

    def test_parse_file_with_strings_in_first_line(self):
        # given
        self._write_to_file('test,1,2')
        # expect
        self.assertRaisesParseError(r'Non-base 10')

    def test_parse_file_with_missing_first_line(self):
        # given
        self._write_to_file('1,,3')
        # expect
        self.assertRaisesParseError(r'missing a value')

    def test_parse_file_with_bad_counts(self):
        # given
        self._write_to_file('0,-1,-1')
        # expect
        self.assertRaisesParseError(r'skills must be positive\.\s.*'
                                    r'experts must be non-negative\.\s.*'
                                    r'projects must be non-negative')

    def test_parse_file_with_non_binary_experts(self):
        # given
        self._write_to_file("""4,2,1
        1,0,1,1
        4,3,5,3
        6,5,6,2""")
        # expect
        self.assertRaisesParseError(r'Expert vectors must be binary')

    def test_parse_file_with_missing_projects(self):
        # given
        self._write_to_file("""4,1,3
        1,0,1,0
        3,3,3,3""")
        # expect
        self.assertRaisesParseError(r'end-of-file')

    def test_parse_file_with_short_vectors(self):
        # given
        self._write_to_file("""2,2,1
        1
        1,0
        1,2""")
        # expect
        self.assertRaisesParseError(r'2 arguments expected, got 1')

    def test_parse_file_with_negative_projects(self):
        # given
        self._write_to_file("""4,1,1
        1,0,0,1
        -5,3,2,1""")
        # expect
        self.assertRaisesParseError(r'Project vectors must be non-negative')

    def test_parse_correct_file(self):
        # given
        self._write_to_file("""4,2,3
        1,0,0,1
        1,0,1,0
        3,2,3,2
        1,0,5,4
        1,2,3,4""")
        # when
        data = self.parser.parse(self.test_file)
        # then
        self.assertEqual(data.skill_count, 4)
        self.assertEqual(data.expert_count, 2)
        self.assertEqual(data.project_count, 3)
        self.assertEqual(data.experts, [[1, 0, 0, 1], [1, 0, 1, 0]])
        self.assertEqual(data.projects, [[3, 2, 3, 2], [1, 0, 5, 4], [1, 2, 3, 4]])

    def tearDown(self):
        self.test_file.close()
        shutil.rmtree(self.test_directory)
