from ..models import db
from ..utils import authutils, strutils, templateutils, valutils


def format_confirm_project(project_id):
    """Format the confirm project interface.

    Returns
    -------
    result : str
        The HTML to display.
    """
    jenv = templateutils.get_jenv()
    is_valid, status_messages = valutils.validate_project_id(project_id)
    user = authutils.get_kerberos()
    can_edit = authutils.can_edit(user, project_id)
    authlink = authutils.get_auth_url(True)
    deauthlink = authutils.get_auth_url(False)
    can_add = authutils.can_add(user)

    project_info = db.get_all_info_for_project(project_id)
    project_info = strutils.decode_utf_nested_dict_list(project_info)

    result = (
        jenv.get_template("pages/confirmproject.html")
        .render(
            user=user,
            is_valid=is_valid,
            validation_status=(
                strutils.html_listify(status_messages) if not is_valid else ""
            ),
            can_edit=can_edit,
            help_address="sipb-projectdb-team [at] mit [dot] edu",
            authlink=authlink,
            project_info=project_info,
            project_id=project_id,
            deauthlink=deauthlink,
            can_add=can_add,
            operation="Submit",
        )
        .encode("utf-8")
    )
    return result


def view(arguments):
    """Display the confirm project interface."""
    project_id = arguments.get("project_id", "")
    return format_confirm_project(project_id)
