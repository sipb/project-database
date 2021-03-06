import cgi


def is_email(text):
    """Determine if a given string is (likely) an email address.

    Currently uses a very simple heuristic.

    Parameters
    ----------
    text : str
        The string to analyze.

    Returns
    -------
    is_email : bool
        Whether or not the string appears to be an email address.
    """
    return text.count('@') == 1


def obfuscate_email(email):
    """Obfuscate an email address to mitigate simple spam bots. Things which
    do not appear to be email addresses are not obfuscated.

    Parameters
    ----------
    email : str
        The raw email address.

    Returns
    -------
    email_obfuscated : str
        The obfuscated email address.
    """
    if is_email(email):
        return email.replace('@', ' [at] ').replace('.', ' [dot] ')
    else:
        return email


def split_comma_sep(input_str):
    """Split a comma-separated list and strip whitespace and blank entries.

    Parameters
    ----------
    input_str : str
        The string to split.

    Returns
    -------
    element_list : list of str
        The elements of input_str, with leading/trailing whitespace stripped.
    """
    result = [s.strip() for s in input_str.split(',')]
    result = [s for s in result if len(s) > 0]
    return result


def html_listify(items):
    """Convert a list of strings to an HTML unordered list.

    Parameters
    ----------
    items : list of str
        The list items.

    Returns
    -------
    result : str
        The HTML list.
    """
    items = [
        cgi.escape(item, quote=True) for item in items
    ]
    result = '<ul>\n'
    for item in items:
        result += '    <li>%s</li>\n' % item
    result += '</ul>\n'
    return result


def is_mit_email(email):
    """Check whether a given string is an MIT email address, including
    *@*.mit.edu addresses.

    NOTE: only checks the ending -- does not actually check if this is a valid
    address!

    Parameters
    ----------
    email : str
        The email address to check.

    Returns
    -------
    is_mit : bool
        Whether or not the address is an MIT address.
    """
    return email.lower().endswith('mit.edu') and (email.count('@') == 1)


def is_plain_mit_email(email):
    """Check whether a given string is an MIT email address of the form
    *@mit.edu.

    NOTE: only checks the ending -- does not actually check if this is a valid
    address!

    Parameters
    ----------
    email : str
        The email address to check.

    Returns
    -------
    is_mit : bool
        Whether or not the address is an MIT address.
    """
    return email.lower().endswith('@mit.edu') and (email.count('@') == 1)


def make_url_absolute(url):
    """Make a URL absolute (with HTTP scheme), if it is not an HTTP/HTTPS URL
    already.

    Parameters
    ----------
    url : str
        The URL to modify.

    Returns
    -------
    url_updated : str
        The absolute URL.
    """
    if not (
        url.lower().startswith('http://') or url.lower().startswith('https://')
    ):
        url = 'http://' + url
    return url


def decode_utf_nested_dict_list(args):
    """Decode all strings in a nested list of dicts.
    """
    if type(args) == dict:
        return {
            key: decode_utf_nested_dict_list(value)
            for key, value in args.items()
        }
    elif type(args) == list:
        return [decode_utf_nested_dict_list(value) for value in args]
    else:
        try:
            return args.decode('utf-8')
        except AttributeError:
            return args
