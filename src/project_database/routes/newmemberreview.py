from ..models import db
from ..utils import authutils, templateutils


def format_new_member_review_list():
    """Format the new member form submission review listing.

    Returns
    -------
    result : str
        The HTML to display.
    """
    jenv = templateutils.get_jenv()
    user = authutils.get_kerberos()
    can_approve = authutils.can_approve(user)
    authlink = authutils.get_auth_url(True)
    deauthlink = authutils.get_auth_url(False)
    can_add = authutils.can_add(user)

    submissions = db.get_all_new_member_submissions() if can_approve else []

    result = (
        jenv.get_template("pages/newmemberreview.html")
        .render(
            user=user,
            can_approve=can_approve,
            can_add=can_add,
            help_address="sipb-projectdb-team [at] mit [dot] edu",
            authlink=authlink,
            deauthlink=deauthlink,
            submissions=submissions,
        )
        .encode("utf-8")
    )
    return result


def view():
    """Display the new member form submission review listing."""
    return format_new_member_review_list()
