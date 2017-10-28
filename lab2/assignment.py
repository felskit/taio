import argparse
import sys

from lab2.parse_input import Parser, ParseError


def init_parser():
    parser = argparse.ArgumentParser(description='Solves the expert-project assignment problem.')
    parser.add_argument('filename',
                        nargs=1,
                        type=str,
                        help='specify the file containing the input data for the problem')
    return parser


def main():
    arg_parser = init_parser()
    args = arg_parser.parse_args()
    input_parser = Parser()
    input_data = None
    try:
        with open(args.filename[0], 'r') as input_file:
            input_data = input_parser.parse(input_file)
    except (IOError, ParseError) as e:
        sys.stderr.write('Error parsing file \'{}\': {}\n'
                         .format(args.filename[0], e))
        exit(1)
    print(input_data.experts)
    print(input_data.projects)


if __name__ == '__main__':
    main()