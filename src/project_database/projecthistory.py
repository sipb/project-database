from . import authutils, db, strutils, templateutils


def format_project_history(project_history, project_id):
    """Format a list of project revisions into an HTML page.

    Parameters
    ----------
    project_history : list of dict
        The project revisions to list.

    Returns
    -------
    result : str
        The HTML to display.
    """
    jenv = templateutils.get_jenv()
    user = authutils.get_kerberos()
    user_email = authutils.get_email()
    authlink = authutils.get_auth_url(True)
    deauthlink = authutils.get_auth_url(False)
    can_add = authutils.can_add(user)
    can_edit = authutils.can_edit(user, project_id)

    result = (
        jenv.get_template("projecthistory.html")
        .render(
            project_history=project_history,
            user=user,
            user_email=user_email,
            authlink=authlink,
            deauthlink=deauthlink,
            can_add=can_add,
            can_edit=can_edit,
            project_id=project_id,
        )
        .encode("utf-8")
    )
    return result


def view(arguments):
    """Display the info for all project revisions."""
    project_id = arguments.get("project_id")
    # TODO: this should show a proper error page
    if project_id is None:
        raise RuntimeError("No project ID specified!")

    project_history = db.get_project_history(project_id)
    project_history = strutils.decode_utf_nested_dict_list(project_history)
    return format_project_history(project_history, project_id)
