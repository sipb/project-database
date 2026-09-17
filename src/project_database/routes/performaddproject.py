import traceback

from ..models import db
from ..services import mail
from ..utils import authutils, formutils, performutils, strutils, valutils


def view(arguments):
    """Respond to an add project request, displaying the appropriate status
    message.
    """
    project_info = formutils.args_to_dict(arguments)
    is_ok, status_messages = valutils.validate_add_project(project_info)

    if is_ok:
        requestor_kerberos = authutils.get_kerberos()
        requires_approval = authutils.requires_approval(requestor_kerberos)
        initial_approval = "awaiting_approval" if requires_approval else "approved"
        try:
            project_id = db.add_project(
                project_info,
                authutils.get_kerberos(),
                initial_approval=initial_approval,
            )
            assert project_id != -1
            project_info["project_id"] = project_id
        except Exception:  # noqa: BLE001
            is_ok = False
            status = ""
            status += "add_project failed with the following exception:\n"
            status += traceback.format_exc()
            status_messages = [status]

    if is_ok:
        if requires_approval:
            message = (
                "The following project details have been sent to the "
                "moderators for approval. You will be notified once the "
                "posting has been reviewed."
            )
            mail.send_to_approvers(project_info)
        else:
            message = None

        page = performutils.format_success_page(
            project_id, "Add Project", message=message
        )
    else:
        page = performutils.format_failure_page(
            strutils.html_listify(status_messages), "Add Project"
        )

    return page
