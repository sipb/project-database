def obfuscate_email(email):
    """Obfuscate an email address to mitigate simple spam bots.

    Parameters
    ----------
    email : str
        The raw email address.

    Returns
    -------
    email_obfuscated : str
        The obfuscated email address.
    """
    return email.replace('@', ' [at] ').replace('.', ' [dot] ')


def split_comma_sep(input_str):
    """Split a comma-separated list and strip whitespace.

    Parameters
    ----------
    input_str : str
        The string to split.

    Returns
    -------
    element_list : list of str
        The elements of input_str, with leading/trailing whitespace stripped.
    """
    return [s.strip() for s in input_str.split(',')]


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
    result = '<ul>\n'
    for item in items:
        result += '    <li>%s</li>\n' % item
    result += '</ul>\n'
    return result
