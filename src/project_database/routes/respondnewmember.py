from ..models import db
from ..utils import authutils, strutils, templateutils, valutils


def format_respond_new_member(submission_id):
    """Format the respond-to-new-member interface.

    Returns
    -------
    result : str
        The HTML to display.
    """
    jenv = templateutils.get_jenv()
    is_valid, status_messages = valutils.validate_new_member_submission_id(
        submission_id
    )
    user = authutils.get_kerberos()
    can_approve = authutils.can_approve(user)
    authlink = authutils.get_auth_url(True)
    deauthlink = authutils.get_auth_url(False)
    can_add = authutils.can_add(user)

    if is_valid and can_approve:
        submission = db.get_new_member_submission(submission_id)
        submission = strutils.decode_utf_nested_dict_list(submission)
        all_projects = strutils.decode_utf_nested_dict_list(
            db.get_all_project_info(filter_method="approved")
        )
        suggested_ids = {
            project["project_id"] for project in submission["suggested_projects"]
        }
    else:
        submission = None
        all_projects = []
        suggested_ids = set()

    result = (
        jenv.get_template("pages/respondnewmember.html")
        .render(
            user=user,
            is_valid=is_valid,
            validation_status=(
                strutils.html_listify(status_messages) if not is_valid else ""
            ),
            can_approve=can_approve,
            help_address="sipb-projectdb-team [at] mit [dot] edu",
            authlink=authlink,
            deauthlink=deauthlink,
            can_add=can_add,
            submission=submission,
            submission_id=submission_id,
            all_projects=all_projects,
            suggested_ids=suggested_ids,
        )
        .encode("utf-8")
    )
    return result


def view(arguments):
    """Display the respond-to-new-member interface."""
    submission_id = arguments.get("submission_id", "")
    return format_respond_new_member(submission_id)
