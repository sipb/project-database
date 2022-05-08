import authutils
import db
import strutils
import templateutils


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
