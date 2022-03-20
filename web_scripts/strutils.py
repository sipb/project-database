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
            obfuscate_email(channel) for channel in project['comm_channels']
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


# def make_url_absolute(url):
#     """Make a URL absolute (with HTTP scheme), if it is not an HTTP/HTTPS URL
#     already.
#     """
#     if not (url.startswith('http://') or url.startswith('https://')):
#         url = 'http://' + url
#     return url


# def make_project_info_dicts_links_absolute(project_list):
#     """Make all of the links for all of the projects in a list of project info
#     dicts absolute.
#     """
#     for project in project_list:
#         project['links'] = [
#             make_url_absolute(link) for link in project['links']
#         ]
