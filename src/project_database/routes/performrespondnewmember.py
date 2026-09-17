import traceback

from ..models import db
from ..services import mail
from ..utils import authutils, formutils, performutils, strutils, valutils


def view(arguments):
    """Respond to a new member form submission with suggested projects and
    reviewer notes, displaying the appropriate status message.
    """
    submission_id = arguments.get("submission_id", "")
    reviewer_notes = arguments.get("reviewer_notes", "").strip()
    suggested_project_ids = formutils.suggested_project_ids_from_arguments(arguments)
    reviewer_kerberos = authutils.get_kerberos()

    is_ok, status_messages = valutils.validate_new_member_response(
        submission_id, suggested_project_ids
    )

    if is_ok:
        try:
            submission_info = db.mark_new_member_submission_reviewed(
                submission_id,
                reviewer_kerberos,
                reviewer_notes,
                suggested_project_ids,
            )
        except Exception:  # noqa: BLE001
            is_ok = False
            status = ""
            status += (
                "mark_new_member_submission_reviewed failed with the "
                "following exception:\n"
            )
            status += traceback.format_exc()
            status_messages = [status]

    if is_ok:
        mail.send_new_member_suggestions(
            submission_info,
            submission_info["suggested_projects"],
            reviewer_kerberos,
            reviewer_notes,
        )
        page = performutils.format_generic_success_page(
            "Response Sent",
            "Your suggestions have been emailed to the new member.",
        )
    else:
        page = performutils.format_failure_page(
            strutils.html_listify(status_messages), "Respond to New Member"
        )

    return page
