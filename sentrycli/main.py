import logging

import argh


from sentrycli.group import group
from sentrycli.query import query


def main():
    argh.dispatch_commands([query, group])


if __name__ == '__main__':
    main()
