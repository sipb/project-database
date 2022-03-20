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


def obfuscate_project_info_dicts(project_list):
    """Obfuscate the comm_channels and contacts fields of all projects in the
    provided list.
    """
    for project in project_list:
        project['comm_channels'] = [
            obfuscate_email(channel['commchannel'])
            for channel in project['comm_channels']
        ]
        for contact in project['contacts']:
            contact['email'] = obfuscate_email(contact['email'])
    return project_list


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


def is_mit_email(email):
    """Check whether a given string is an MIT email address.

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
    return email.endswith('@mit.edu') and (email.count('@') == 1)
