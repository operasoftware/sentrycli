from argh import CommandError


def check_required_keys_present(required, dictionary):
    """
    Check if at least one of required values are present in dictionary.
    :type required: list
    :param dictionary: dictionary which should be checked.
    :type: dict
    :raises: argh.CommandError
    """
    if all([dictionary.get(param) is None for param in required]):
        raise CommandError('one of %s has to be specified' % '|'.join(required))
