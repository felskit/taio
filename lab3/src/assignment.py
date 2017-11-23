import argparse
import sys

from src.utils.parser import Parser, ParseError
from src.utils.handler import GeneticHandler


def init_parser():
    """
    Constructs an instance of :class:`argparse.ArgumentParser` configured for the program.

    The returned :class:`argparse.ArgumentParser` accepts one positional string argument, which is the input
    file name.
    """
    parser = argparse.ArgumentParser(description='Solves the expert-project assignment problem.')
    parser.add_argument('filename',
                        nargs=1,
                        type=str,
                        help='specify the file containing the input data for the problem')
    return parser


def main():
    """The main program entry point."""
    arg_parser = init_parser()
    args = arg_parser.parse_args()
    input_parser = Parser()
    scheduling_data = None
    try:
        with open(args.filename[0], 'r') as input_file:
            scheduling_data = input_parser.parse(input_file)
    except (IOError, ParseError) as e:
        sys.stderr.write('Error parsing file \'{}\': {}\n'
                         .format(args.filename[0], e))
        exit(1)
    print(GeneticHandler(scheduling_data, 2137).solve())


if __name__ == '__main__':
    main()
