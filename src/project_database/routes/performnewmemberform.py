import traceback

from ..models import db
from ..services import mail
from ..utils import authutils, formutils, performutils, strutils, valutils


def view(arguments):
    """Respond to a new member form submission, displaying the appropriate
    status message.
    """
    submission_info = formutils.new_member_form_to_dict(arguments)
    is_ok, status_messages = valutils.validate_new_member_form(submission_info)

    if is_ok:
        kerberos = authutils.get_kerberos()
        submission_info["kerberos"] = kerberos
        submission_info["email"] = authutils.get_email()
        try:
            submission_id = db.add_new_member_submission(submission_info, kerberos)
            submission_info["submission_id"] = submission_id
        except Exception:  # noqa: BLE001
            is_ok = False
            status = ""
            status += "add_new_member_submission failed with the following exception:\n"
            status += traceback.format_exc()
            status_messages = [status]

    if is_ok:
        mail.send_new_member_notification_to_approvers(submission_info)
        page = performutils.format_generic_success_page(
            "New Member Form Submitted",
            "Thanks for filling out the new member form! A SIPB member will "
            "review your responses and follow up with some project "
            "suggestions by email.",
        )
    else:
        page = performutils.format_failure_page(
            strutils.html_listify(status_messages), "New Member Form"
        )

    return page
