from .. import config
from ..utils import authutils, templateutils


def format_new_member_form():
    """Format the new member form interface.

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
    result = (
        jenv.get_template("pages/newmemberform.html")
        .render(
            user=user,
            user_email=user_email,
            can_add=can_add,
            help_address="sipb-projectdb-team [at] mit [dot] edu",
            authlink=authlink,
            deauthlink=deauthlink,
            interest_options=config.NEW_MEMBER_INTEREST_OPTIONS,
            experience_levels=config.NEW_MEMBER_EXPERIENCE_LEVELS,
        )
        .encode("utf-8")
    )
    return result


def view():
    """Display the new member form interface."""
    return format_new_member_form()
