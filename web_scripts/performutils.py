import authutils
import db
import strutils
import templateutils


def check_for_name_change(project_info, project_id):
    """Check if the project name in the provided project_info dict matches the
    name in the database. The check is case-insensitive.

    Parameters
    ----------
    project_info : dict
        The project info extracted from the form.
    project_id : int
        The project ID.

    Returns
    -------
    is_changed : bool
        Whether or not the project name in the provided project_info dict
        matches the name in the database.
    """
    return (
        project_info['name'].lower() != db.get_project_name(project_id).lower()
    )


def nullable_case_insensitive_equals(a, b):
    """Compare nullable strings for case-insensitive equality.

    None is treated as being equivalent to an empty string.

    Parameters
    ----------
    a, b : str or None
        The strings to compare.

    Returns
    -------
    is_equal : bool
        Whether or not the two strings are equal.
    """
    if (a is None) and (b is None):
        return True
    elif (a is not None) and (b is not None):
        return a.lower() == b.lower()
    elif (a is None) and (b is not None) and (len(b) == 0):
        return True
    elif (b is None) and (a is not None) and (len(a) == 0):
        return True
    else:
        return False


def check_for_info_change(project_info, project_id):
    """Check if the fields in the provided project_info dict have changed from
    the values in the database. The check is case-insensitive.

    Parameters
    ----------
    project_info : dict
        The project info extracted from the form.
    project_id : int
        The project ID.

    Returns
    -------
    is_changed : bool
        Whether or not the project details in the provided project_info dict
        match those in the database.
    """
    # TODO: Would be better for this to crawl the schema and build the checks
    # automatically...
    db_project_info = db.get_all_info_for_project(project_id)

    if db_project_info['name'].lower() != project_info['name'].lower():
        return True

    if (
        db_project_info['description'].lower() !=
        project_info['description'].lower()
    ):
        return True

    if db_project_info['status'] != project_info['status']:
        return True

    if len(db_project_info['links']) != len(project_info['links']):
        return True
    else:
        for db_link, link in zip(
            db_project_info['links'], project_info['links']
        ):
            if db_link['link'].lower() != link['link'].lower():
                return True

            if db_link['index'] != link['index']:
                return True

            if not nullable_case_insensitive_equals(
                db_link['anchortext'], link['anchortext']
            ):
                return True

    if (
        len(db_project_info['comm_channels']) !=
        len(project_info['comm_channels'])
    ):
        return True
    else:
        for db_comm_channel, comm_channel in zip(
            db_project_info['comm_channels'], project_info['comm_channels']
        ):
            if (
                db_comm_channel['commchannel'].lower() !=
                comm_channel['commchannel'].lower()
            ):
                return True

            if db_comm_channel['index'] != comm_channel['index']:
                return True

    if len(db_project_info['roles']) != len(project_info['roles']):
        return True
    else:
        for db_role, role in zip(
            db_project_info['roles'], project_info['roles']
        ):
            if db_role['role'].lower() != role['role'].lower():
                return True

            if db_role['description'].lower() != role['description'].lower():
                return True

            if not nullable_case_insensitive_equals(
                db_role['prereq'], role['prereq']
            ):
                return True

            if db_role['index'] != role['index']:
                return True

    if len(db_project_info['contacts']) != len(project_info['contacts']):
        return True
    else:
        for db_contact, contact in zip(
            db_project_info['contacts'], project_info['contacts']
        ):
            if db_contact['type'] != contact['type']:
                return True

            if db_contact['email'].lower() != contact['email'].lower():
                return True

            if db_contact['index'] != contact['index']:
                return True

    return False


def format_success_page(project_id, operation, message=None):
    """Format the success page.

    Parameters
    ----------
    project_id : int
        The ID for the project.

    Returns
    -------
    result : str
        The HTML to display.
    """
    user = authutils.get_kerberos()
    jenv = templateutils.get_jenv()

    project_info = db.get_all_info_for_project(project_id)
    project_info = authutils.enrich_project_list_with_permissions(
        user, [project_info]
    )[0]
    project_info = strutils.decode_utf_nested_dict_list(project_info)
    authlink = authutils.get_auth_url(True)
    deauthlink = authutils.get_base_url(False) + '/projectlist.py'
    can_add = authutils.can_add(user)
    result = ''
    result += 'Content-type: text/html\n\n'
    result += jenv.get_template('performsuccess.html').render(
        project=project_info,
        operation=operation,
        user=user,
        authlink=authlink,
        deauthlink=deauthlink,
        can_add=can_add,
        message=message
    ).encode('utf-8')
    return result


def format_failure_page(status, operation):
    """Format the failure page.

    Parameters
    ----------
    status : str
        The status string explaining why the project was rejected.

    Returns
    -------
    result : str
        The HTML to display.
    """
    jenv = templateutils.get_jenv()
    user = authutils.get_kerberos()
    authlink = authutils.get_auth_url(True)
    deauthlink = authutils.get_base_url(False) + '/projectlist.py'
    can_add = authutils.can_add(user)
    status = strutils.decode_utf_nested_dict_list(status)
    result = ''
    result += 'Content-type: text/html\n\n'
    result += jenv.get_template('performfailure.html').render(
        status=status,
        operation=operation,
        user=user,
        authlink=authlink,
        deauthlink=deauthlink,
        can_add=can_add
    ).encode('utf-8')
    return result
