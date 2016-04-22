import json
import logging
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Preferences(object):
    """
    Holds user's preferences.
    """
    PATH = os.path.expanduser('~/.sentrycli')

    def __init__(self):
        self._prefs = {}
        self.load();

    def load(self):
        logger.info('Loading...')

        if not os.path.isfile(self.PATH):
            logger.info('"%s" is not a regular file. Skipping.', self.PATH)
            return

        with open(self.PATH) as f:
            try:
                self._prefs = json.loads(f.read())
            except ValueError as error:
                logger.exception(error)
                return

        logger.info('Loaded')

    @property
    def host(self):
        return self._prefs.get('host')

    @host.setter
    def host(self, host):
        self._prefs['host'] = host

    @property
    def api_key(self):
        return self._prefs.get('api_key')

    @api_key.setter
    def api_key(self, api_key):
        self._prefs['api_key'] = api_key

    def save(self):
        logger.info('Saving...')

        with open(self.PATH, 'w') as f:
            f.write(json.dumps(self._prefs, indent=4)) 

        logger.info('Saved')
