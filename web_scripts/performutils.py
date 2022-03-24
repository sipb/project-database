import authutils
import strutils
import templateutils


def format_success_page(project_info, operation):
    """Format the success page.

    Parameters
    ----------
    project_info : dict
        The project info which was added to the database.

    Returns
    -------
    result : str
        The HTML to display.
    """
    project_info = strutils.obfuscate_project_info_dicts([project_info])[0]
    project_info = strutils.make_project_info_dicts_links_absolute(
        [project_info]
    )[0]
    jenv = templateutils.get_jenv()
    user = authutils.get_kerberos()
    project_info['can_edit'] = authutils.can_edit(
        user, project_info['project_id']
    )
    authlink = authutils.get_auth_url(True)
    deauthlink = authutils.get_auth_url(False)
    can_add = authutils.can_add(user)
    result = ''
    result += 'Content-type: text/html\n\n'
    result += jenv.get_template('performsuccess.html').render(
        project=project_info,
        operation=operation,
        user=user,
        authlink=authlink,
        deauthlink=deauthlink,
        can_add=can_add
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
    deauthlink = authutils.get_auth_url(False)
    can_add = authutils.can_add(user)
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
