from datetime import datetime
from urlparse import urljoin
import json
import logging
import os
import pickle
import sys

from argh import arg
from argh.exceptions import CommandError
from dateutil.parser import parse as datetime_parse
from dateutil.tz import tzlocal
import requests

from sentrycli.constants import DEFAULT_API_VERSION
from sentrycli.preferences import Preferences


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_api_key(key, version, host):
    """
    Check if API key is valid.

    :param key: API key
    :type: str
    :param version: API version
    :type: int
    :param host:
    :type: str
    :rtype: bool
    """
    url = urljoin(host, 'api/%d/' % version)
    response = requests.get(url, auth=(key, ''))

    if not response.ok:
        detail = response.json()['detail']
        logger.error('Something is not right with API key: %s', detail)
        return False
    else:
        logger.info('API key is fine')
        return True


def get_events(url, api_key, limit, since=None, to=None):
    """
    Get issue's events by URL.
    Handle pagination automatically -
    https://docs.getsentry.com/on-premise/api/pagination/.

    :param url: URL to get events
    :type: str
    :param key: API key
    :type: str
    :param limit: Maximum number of events to return
    :type: int
    :param since: event's min creation datetime
    :type: datetime
    :param to: event's max creation datetime
    :type: datetime
    :rtype: list
    """
    response = requests.get(url, auth=(api_key, ''))

    if not response.ok:
        code = response.status_code

        if code == 404:
            logger.error('Issue not found')
            return []

        detail = response.json()['detail']
        logger.error('Server returned %d: %s', code, detail)
        return []

    if (since or to) is not None:
        events = []

        for event in response.json():
            created = datetime_parse(event['dateCreated'])

            if since is not None and created < since:
                # Set limit to avoid asking for more pages.
                limit = len(events)
                break

            if to is not None and created > to:
                continue

            events.append(event)
    else:
        events = response.json()

    limit -= len(events)

    if limit < 0:
        events = events[:limit]
        limit = 0

    if limit > 0 and response.links['next']['results'] == 'true':
        events.extend(get_events(url=response.links['next']['url'],
                                 api_key=api_key,
                                 limit=limit,
                                 since=since,
                                 to=to))

    return events



@arg('issue', help='Issue identifier')
@arg('--api-key', help='API key')
@arg('--host', help='Host')
@arg('--api-version', help='API version')
@arg('-s', '--since', help="format 'yyyy-mm-dd(Thh:mm:ss)'",
     type=datetime_parse)
@arg('-t', '--to', help="format 'yyyy-mm-dd(Thh:mm:ss)'", type=datetime_parse)
@arg('-o', '--output', help='path to output file')
@arg('-f', '--format', help='output file format', choices=['json', 'pickle'])
@arg('-l', '--limit', help='max number of downloaded events')
def query(issue, api_key=None, host=None, api_version=DEFAULT_API_VERSION,
          output=None, format='json', limit=sys.maxint,
          to=datetime.now(tzlocal()), since=None):

    preferences = Preferences()

    if since is not None and since.tzinfo is None:
        since = since.replace(tzinfo=tzlocal())

    if to.tzinfo is None:
        to = to.replace(tzinfo=tzlocal())

    if host is None:
        host = preferences.host

        if host is None:
            logger.info('Host not found in saved preferences')
            raise CommandError('Host not specified (--host)')
        else:
            logger.info('Host found in saved preferences')

    else:
        preferences.host = host

    if api_key is None:
        api_key = preferences.api_key

        if api_key is None:
            logger.info('API key not found in saved preferences')
            raise CommandError('API key not specified (--api-key)')
        else:
            logger.info('API key found in saved preferences')
    else:
        preferences.api_key = api_key

    if output is None:
        file_name = issue
        file_name += '.' + format
        output = os.path.join(os.getcwd(), file_name)

    ret = check_api_key(key=api_key,
                        host=host,
                        version=api_version)

    if not ret:
        return

    path = '/api/%d/issues/%s/events/' % (api_version, issue)
    url = urljoin(host, path)
    logger.info('Getting events for issue %s (may take a while)', issue)
    events = get_events(url=url,
                        api_key=api_key,
                        limit=limit,
                        since=since,
                        to=to)

    if len(events) == 0:
        logger.info('No events found')
        return

    with open(output, 'w+') as f:
        if format == 'json':
            json.dump(events, f, indent=2)
        else:
            pickle.dump(events, f)

    logger.info('%d events saved to %s', len(events), output)
