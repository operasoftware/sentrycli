import argparse
import logging

from argh.constants import PARSER_FORMATTER
import argh

from sentrycli import __version__
from sentrycli.group import group
from sentrycli.query import query


def main():
    parser = argparse.ArgumentParser(formatter_class=PARSER_FORMATTER)
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + __version__)
    argh.add_commands(parser, [query, group])
    argh.dispatch(parser)


if __name__ == '__main__':
    main()
