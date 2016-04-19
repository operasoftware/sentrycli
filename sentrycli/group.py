from collections import Counter
from itertools import izip_longest
import json
import logging

from argh import arg, dispatching, CommandError
from prettytable import PrettyTable
from progressbar import ProgressBar


logging.basicConfig(level=logging.INFO)


def get_event_headers(event):
    """
    Get event's HTTP headers.

    :param event: event to process
    :type: dict
    :rtype: dict
    """
    for entry in event['entries']:
        if entry['type'] == 'request':
            return dict(entry['data']['headers'])

    return {}


def get_event_params(event):
    """
    Get event message's parameters.

    :param event: event to process.
    :type: dict
    :rtype: dict
    """
    for entry in event['entries']:
        if entry['type'] == 'message':
            return entry['data']

    return {}


def get_event_context(event):
    """
    Get event's context.

    :param event: event to process
    :type: dict
    :rtype: dict
    """
    context = event['context'].copy()
    context.update(event.get('user', {}))
    return context


def get_event_frames(event):
    """
    Get event's stack frames.

    :param event: event to process
    :type: dict
    :rtype: list
    """
    for entry in event['entries']:
        if entry['type'] == 'exception':
            # TODO does `entry['data']['values']` have always 1 element?
            return entry['data']['values'][0]['stacktrace']['frames']

    return []


def get_event_vars(event):
    """
    Get event's variables from all its stack frames.

    :param event: event to process
    :type: dict
    :rtype: set
    """
    frames = get_event_frames(event)
    values = set()

    for frame in frames:
        values |= set(frame.get('vars', []))

    return values


def get_event_tags(event):
    """
    Get event's tags.

    :param event: event to process
    :type: dict
    :rtype: dict
    """
    return {tag['key']: tag['value'] for tag in event['tags']}


def get_keys(fun, events):
    keys = set()

    for event in events:
        res = fun(event)

        if res is not None:
            keys |= set(res)

    keys = sorted(keys)
    return keys


def print_options(events):
    """
    Print available aggregration options (headers, context, tags etc.)

    :param events: list of events from which gather attributes
    :type: list(dict)
    """
    headers = get_keys(get_event_headers, events)
    context = get_keys(get_event_context, events)
    params = get_keys(get_event_params, events)
    variables = get_keys(get_event_vars, events)
    tags = get_keys(get_event_tags, events)

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
@arg('--tags', help='tags', nargs='+')
@arg('-o', '--options', help='list possible grouping options')
def group(pathname, headers=None, context=None, params=None,
          variables=None, tags=None, options=False):
    with open(pathname) as f:
        events = json.load(f)

    if options:
        print_options(events)
        return

    keys = headers or context or params or variables or tags

    if keys is None:
        raise CommandError('one of headers|params|context|vars|tags '
                           'has to be specified')

    keys = sorted(keys)

    if [headers, context, params, variables, tags].count(None) < 4:
        raise CommandError(
            'only one of headers|params|context|vars|tags can be specified')

    values = Counter()

    with ProgressBar(maxval=len(events)) as progress_bar:
        for index, event in enumerate(events):
            meta = {}

            if headers is not None:
                for header in headers:
                    headers = get_event_headers(event)
                    meta[header] = headers.get(header)
            elif context is not None:
                context = get_event_context(event)

                for var in context:
                    meta[var] = context.get(var)
            elif params is not None:
                params = get_event_params(event)

                for param in params:
                    meta[param] = params.get(param)
            elif tags is not None:
                tags = get_event_tags(event)

                for tag in tags:
                    meta[tag] = tags.get(tag)
            else:
                for var in variables:
                    for frame in get_event_frames(event):
                        res = frame['vars'].get(var)

                        if res is not None:
                            meta[var] = res
                            break

            value = tuple(meta.get(key) for key in keys)
            values[value] += 1

            progress_bar.update(index)

    print_grouping(keys, values)


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
