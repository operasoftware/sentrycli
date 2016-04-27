from collections import Counter
from datetime import datetime
from itertools import izip_longest
import json
import logging

from argh import arg, dispatching, CommandError
from prettytable import PrettyTable
from progressbar import ProgressBar
from sentrycli.event import Event


logging.basicConfig(level=logging.INFO)


def get_keys(prop, events):
    """
    Get all distinct keys from events' property.
    :rtype: set
    """
    keys = set()

    for event in events:
        res = getattr(event, prop)

        if res is not None:
            keys |= set(res)

    keys = sorted(keys)
    return keys


def print_options(events):
    """
    Print available aggregration options (headers, context, tags etc.)

    :param events: list of events from which gather attributes
    :type: list
    """
    headers = get_keys('headers', events)
    context = get_keys('context', events)
    params = get_keys('params', events)
    variables = get_keys('vars', events)
    tags = get_keys('tags', events)

    table = PrettyTable(['Headers', 'Context', 'Params', 'Vars', 'Tags'])
    table.align = 'l'

    for header, context_var, param, var, tag in izip_longest(
            headers, context, params, variables, tags, fillvalue=''):
        table.add_row((header, context_var, param, var, tag))

    print table


@arg('pathname', help='path to input file')
@arg('--headers', help='headers', nargs='+')
@arg('--context', help='context', nargs='+')
@arg('--params', help='params', nargs='+')
@arg('--variables', help='variables', nargs='+')
@arg('--ctime', help='creation time', choices=('daily', 'monthly'))
@arg('--tags', help='tags', nargs='+')
@arg('-o', '--options', help='list possible grouping options')
def group(pathname, headers=None, context=None, params=None,
          variables=None, tags=None, options=False, ctime=None):
    with open(pathname) as f:
        events = json.load(f)

    events = [Event(event) for event in events]

    if len(events) == 0:
        print 'No events to analyze'

    if options:
        print_options(events)
        return

    keys = headers or context or params or variables or tags or ctime

    if keys is None:
        raise CommandError('one of headers|params|context|vars|tags|ctime '
                           'has to be specified')

    keys = sorted(keys)

    if [headers, context, params, variables, tags, ctime].count(None) < 5:
        raise CommandError(
            'only one of headers|params|context|vars|tags|ctime can be specified')

    if ctime is not None:
        group_by_ctime(events, ctime)
        return

    values = Counter()

    with ProgressBar(maxval=len(events)) as progress_bar:
        for index, event in enumerate(events):
            meta = {}

            if headers is not None:
                for header in headers:
                    meta[header] = event.headers.get(header)
            elif context is not None:
                for var in context:
                    meta[var] = event.context.get(var)
            elif params is not None:
                for param in params:
                    meta[param] = event.params.get(param)
            elif tags is not None:
                for tag in tags:
                    meta[tag] = event.tags.get(tag)
            else:
                for var in variables:
                    for frame in event.frames:
                        res = frame['vars'].get(var)

                        if res is not None:
                            meta[var] = res
                            break

            value = tuple(meta.get(key) for key in keys)
            values[value] += 1

            progress_bar.update(index)

    print_grouping(keys, values)


def group_by_ctime(events, mode):
    """
    Group events by creation time.
    :param events: events to group
    :type: list
    :param mode: grouping mode (daily or monthly)
    :type: str
    """
    counter = Counter()
    total = 0

    for event in events:
        if mode == 'daily':
            day = event.ctime.day
        elif mode == 'monthly':
            day = 1

        key = datetime(event.ctime.year, event.ctime.month, day)

        counter[key] += 1
        total += 1

    if mode == 'daily':
        fmt = '%Y-%m-%d'
        title = 'day'
    elif mode == 'monthly':
        fmt = '%Y-%m'
        title = 'month'

    table = PrettyTable([title, 'count', '%'])
    total = sum(counter.values())

    for item in sorted(counter.items()):
        table.add_row((item[0].strftime(fmt),
                       item[1],
                       item[1] * 100.0 / total))

    table.align['count'] = 'r'
    table.align['%'] = 'r'
    table.float_format['%'] = '.1'
    print table


def print_grouping(attributes, grouping):
    """
    Print computed groups.

    :param attributes: list of grouped attributes
    :type: list(str)
    :param values: counter for each combination of attributes' values
    :type: Counter
    """
    table = PrettyTable(attributes + ['count', '%'])
    table.align = 'l'
    table.align['count'] = 'r'
    table.align['%'] = 'r'
    table.float_format['%'] = '.1'

    total = sum(grouping.values())

    for keys, count in grouping.items():
        table.add_row(keys + (count, count * 100.0 / total))

    print '\n', table.get_string(sortby='count', reversesort=True)
    print 'Total:', total
