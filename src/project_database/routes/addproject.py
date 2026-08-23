from ..utils import authutils, templateutils


def format_add_project():
    """Format the add project interface.

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
    result = (
        jenv.get_template("pages/addproject.html")
        .render(
            user=user,
            can_add=can_add,
            help_address="sipb-projectdb-team [at] mit [dot] edu",
            authlink=authlink,
            deauthlink=deauthlink,
            operation="Create project",
        )
        .encode("utf-8")
    )
    return result


def view():
    """Display the add project interface."""
    return format_add_project()
