import logging
from argparse import ArgumentTypeError
from collections import Counter, defaultdict

from argh import arg, CommandError

from sentrycli.event import load_from_file
from sentrycli.table import Table

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_breadcrumbs_categories_with_attributes(events):
    """
    Get breadcrumbs attributes grouped by categories.
    :type events: list<Event>
    :rtype: defaultdict<str: set>
    """
    categories = defaultdict(set)

    for event in events:
        for breadcrumb in event.breadcrumbs:
            attributes = categories[breadcrumb['category']]
            attributes |= set(breadcrumb)
            try:
                attributes |= {'data.%s' % extra for extra in
                               breadcrumb['data']}
                attributes |= {'data.%s' % extra for extra in
                               breadcrumb['data']['extra']}
            except (TypeError, KeyError):
                pass

            attributes.discard('category')
            attributes.discard('data')
            attributes.discard('data.extra')

    return categories


def print_options(events):
    """
    Print available breadcrumbs aggregation options.

    :param events: list of events from which gather attributes
    :type: list
    """
    categories = get_breadcrumbs_categories_with_attributes(events)
    table = Table(['Categories', 'Attributes'], hrules=1)

    for category, attributes in categories.items():
        table.add_row([category, '\n'.join(attributes)])
    print table


def parse_attribute(attr):
    try:
        category, attr = attr.split(':')
    except ValueError:
        raise ArgumentTypeError('should be in format <category>:<attribute>')
    return category, attr


@arg('pathname', help='path to input file')
@arg('--top', type=int, help='show only top x results')
@arg('-o', '--options', help='list possible grouping options')
@arg('-a', '--attributes', nargs='+', type=parse_attribute,
     help='attributes to group breadcrumbs, format: <category>:<attr>')
def breadcrumbs(pathname, attributes=None, top=None, options=False):
    """
    Analyze and filter event's attributes
    """
    events = load_from_file(pathname)

    if options:
        print_options(events)
        return

    if attributes is None:
        raise CommandError('--attributes argument is mandatory')

    if attributes:
        group_by_attributes(events, attributes, top)


def group_by_attributes(events, attributes, top):
    """
    Group events by specified breadcrumb attributes.
    :param events: events to group
    :type: list
    :param attributes: attributes which we want to analyze
    :type: list
    :param top: show only that much results
    :type: int
    """
    values = Counter()
    column_order = [attribute[1] for attribute in attributes]

    for event in events:
        found = {}

        for attribute in attributes:
            category, attribute_name = attribute
            attribute_keys = attribute_name.split('.')
            key = attribute_keys[0]
            data_key = attribute_keys[1] if len(
                attribute_keys) > 1 else None

            for breadcrumb in event.breadcrumbs:
                if breadcrumb['category'] != category:
                    continue

                if key not in breadcrumb:
                    logger.error('Invalid breadcrumb attribute %s', key)
                    exit(1)

                value = breadcrumb.get(key)

                if data_key is not None and value is not None:
                    data = value.get('extra', value)
                    value = data.get(data_key)
                found[attribute_name] = value

        for attribute in attributes:
            category, attribute_name = attribute
            if attribute_name not in found:
                found[attribute_name] = '<NOT PRESENT>'

        if found:
            values[tuple(found[key] for key in column_order)] += 1

    table = Table(attributes + ['count', '%'])
    table.add_rows(len(events), values.most_common(top))
    print '\n' + table.by_count()
