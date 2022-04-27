import strutils


def safe_cgi_field_get(arguments, field, default=''):
    """Get a field from CGI arguments, with failback for absent fields.

    Parameters
    ----------
    arguments : cgi.FieldStorage
        The data from the form.
    field : str
        The field to get.
    default : str, optional
        The value to use when a field is not present. Default is the empty
        string.

    Returns
    -------
    value : str
        The field value.
    """
    return arguments[field].value if field in arguments else default


def contact_list_to_dict_list(contact_list):
    """Convert a list of contacts to a properly-formatted list of dicts.

    The first entry is assumed to be the primary contact.

    Parameters
    ----------
    contact_list : list of str
        The email addresses for each contact.

    Returns
    -------
    contact_dict_list : list of dict
        The formatted contact dicts with types assigned.
    """
    result = []
    idx = 0
    for contact in contact_list:
        if len(contact) > 0:
            result.append(
                {'email': contact, 'type': 'secondary', 'index': idx}
            )
            idx += 1

    if len(result) > 0:
        result[0]['type'] = 'primary'
    return result


def get_role_ids(arguments):
    """Get all role IDs from the arguments from CGI.

    Parameters
    ----------
    arguments : cgi.FieldStorage
        The data from the form.

    Returns
    -------
    role_ids : list of str
        The role IDs present in the arguments, in the order they are discovered
        in.
    """
    role_ids = set()
    for key in arguments.keys():
        # Check all fields so that we can catch mal-formed inputs:
        if key.startswith('role_name_'):
            role_ids.add(key[len('role_name_'):])
        elif key.startswith('role_description_'):
            role_ids.add(key[len('role_description_'):])
        elif key.startswith('role_prereqs_'):
            role_ids.add(key[len('role_prereqs_'):])
    return list(role_ids)


def extract_roles(arguments):
    """Extract the role dicts from the arguments from CGI.

    Parameters
    ----------
    arguments : cgi.FieldStorage
        The data from the form.

    Returns
    -------
    roles : list of dict
        The information for each role.
    """
    role_ids = get_role_ids(arguments)
    roles = []
    for index, role_id in enumerate(role_ids):
        roles.append(
            {
                'role': safe_cgi_field_get(
                    arguments, 'role_name_' + role_id
                ),
                'description': safe_cgi_field_get(
                    arguments, 'role_description_' + role_id
                ),
                'prereq': safe_cgi_field_get(
                    arguments, 'role_prereqs_' + role_id
                ),
                'index': index
            }
        )
        if len(roles[-1]['prereq']) == 0:
            roles[-1]['prereq'] = None
    return roles


def args_to_dict(arguments):
    """Reformat the arguments from CGI into a dict.

    Parameters
    ----------
    arguments : cgi.FieldStorage
        The data from the form.

    Returns
    -------
    project_info : dict
        The project info dict.
    """
    return {
        'name': safe_cgi_field_get(arguments, 'name'),
        'description': safe_cgi_field_get(arguments, 'description'),
        'status': safe_cgi_field_get(arguments, 'status'),
        'links': [
            strutils.make_url_absolute(link)
            for link in strutils.split_comma_sep(
                safe_cgi_field_get(arguments, 'links')
            )
        ],
        'comm_channels': strutils.split_comma_sep(
            safe_cgi_field_get(arguments, 'comm_channels')
        ),
        'contacts': contact_list_to_dict_list(
            strutils.split_comma_sep(
                safe_cgi_field_get(arguments, 'contacts')
            )
        ),
        'roles': extract_roles(arguments)
    }
