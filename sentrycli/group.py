import logging
import re
from collections import Counter
from datetime import datetime
from itertools import izip_longest

from argh import arg

from sentrycli.event import load_from_file
from sentrycli.table import Table
from sentrycli.utils import check_required_keys_present

logging.basicConfig(level=logging.INFO)


T_HEADER = 'header'
T_CONTEXT = 'context'
T_PARAM = 'param'
T_VAR = 'var'
T_TAG = 'tag'
ORDER_META_KEY = ('breadcrumb', 'breadcrumbs in order')


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

    table = Table(['Headers', 'Context', 'Params', 'Vars', 'Tags'])

    map(table.add_row, izip_longest(headers, context, params, variables, tags,
                                    fillvalue=''))

    print table


@arg('pathname', help='path to input file')
@arg('--headers', help='headers', nargs='+')
@arg('--context', help='context', nargs='+')
@arg('--params', help='params', nargs='+')
@arg('--variables', help='variables', nargs='+')
@arg('--ctime', help='creation time', choices=('daily', 'monthly'))
@arg('--breadcrumbs', nargs='+',
     help='analyze if events order of breadcrumbs categories is fullfiled. '
          'Order should be in Python regex format. Use `.*` for any number of'
          'categories between and ` ` for strict order.')
@arg('--tags', help='tags', nargs='+')
@arg('--top', type=int, help='show only top x results')
@arg('-o', '--options', help='list possible grouping options')
def group(pathname, headers=None, context=None, params=None, breadcrumbs=None,
          variables=None, tags=None, options=False, ctime=None, top=None):

    events = load_from_file(pathname)

    if options:
        print_options(events)
        return

    check_required_keys_present([
        'headers', 'context', 'params', 'variables', 'tags', 'ctime',
        'breadcrumbs'], locals())

    headers = headers or []
    context = context or []
    params = params or []
    variables = variables or []
    tags = tags or []
    breadcrumbs = [re.compile(breadcrumb) for breadcrumb in breadcrumbs or []]

    if ctime is not None:
        group_by_ctime(events, ctime)
        return

    keys = []
    keys.extend([(T_HEADER, header) for header in headers])
    keys.extend([(T_CONTEXT, var) for var in context])
    keys.extend([(T_PARAM, param) for param in params])
    keys.extend([(T_VAR, var) for var in variables])
    keys.extend([(T_TAG, tag) for tag in tags])

    if len(breadcrumbs):
        keys.extend([ORDER_META_KEY])

    values = Counter()

    for event in events:
        meta = {}

        for header in headers:
            meta[(T_HEADER, header)] = event.headers.get(header)

        for var in context:
            meta[(T_CONTEXT, var)] = event.context.get(var)

        for param in params:
            meta[(T_PARAM, param)] = event.params.get(param)

        for tag in tags:
            meta[(T_TAG, tag)] = event.tags.get(tag)

        for var in variables:
            for frame in event.frames:
                res = frame['vars'].get(var)

                if res is not None:
                    meta[(T_VAR, var)] = res
                    break

        if len(breadcrumbs):
            meta[ORDER_META_KEY] = False

            for breadcrumb in breadcrumbs:
                if not event.is_breadcrumbs_order_preserved(breadcrumb):
                    break
            else:
                meta[ORDER_META_KEY] = True

        value = tuple(meta.get(key) for key in keys)
        values[value] += 1

    print_grouping([key[1] for key in keys], values, top)


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

    table = Table([title, 'count', '%'])
    total = sum(counter.values())

    for item in sorted(counter.items()):
        table.add_row((item[0].strftime(fmt),
                       item[1],
                       item[1] * 100.0 / total))

    print table


def print_grouping(attributes, grouping, top):
    """
    Print computed groups.

    :param attributes: list of grouped attributes
    :type: list(str)
    :param grouping: counter for each combination of attributes' values
    :type: Counter
    :type top: int
    """
    total = sum(grouping.values())

    table = Table(attributes + ['count', '%'])
    table.add_rows(total, grouping.most_common(top))

    print '\n' + table.by_count()
    print 'Total:', total
