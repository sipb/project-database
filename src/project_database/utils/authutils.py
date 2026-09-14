# Based on:
# https://github.com/sipb/hwops/blob/master/web_scripts/kerbparse.py
# https://github.com/sipb/hwops/blob/master/web_scripts/main.py
# https://github.com/sipb/hwops/blob/master/web_scripts/moira.py


from flask import current_app, request, session

from .. import config
from ..models import db
from ..services import roster


def get_kerberos():
    """Get the kerberos of the user. Returns None if there is no user.

    Returns
    -------
    kerberos : str
        The kerberos (username only) for the user.
    """
    email = get_email()
    if email:
        return email[: email.index("@")]
    else:
        return None


def get_email():
    """Get the email of the user. Returns None if there is no user.

    Returns
    -------
    email : str
        The email for the user.
    """
    email = request.environ.get("SSL_CLIENT_S_DN_Email")

    if current_app.debug and not email:
        email = session.get("debug_email")
    
    if (
        (email is None)
        or (not email.lower().endswith("@mit.edu"))
        or (email.count("@") != 1)
    ):
        return None
    else:
        return email


def get_auth_url(do_authenticate):
    """Get the authentication URL. If debug is enabled, then will get debug auth.

    Parameters
    ----------
    do_authenticate : bool
        If true, then the login URL, else the logout URL

    Returns
    -------
    url : str
        The authentication URL.
    """
    if current_app.debug:
        base = request.host_url.rstrip("/")
        return f"{base}/authdebug"
    
    return "/hlogin" if do_authenticate else "/hlogout"

def is_sipb(user):
    if user:
        return user in roster.sipb_roster
    else:
        return False


def is_keyholder(user):
    # NOTE: the roster uses the older "prospective" vs. "member" distinction,
    # rather than "member" vs. "keyholder".
    if user:
        return roster.sipb_roster.get(user, "other") == "member"
    else:
        return False


def can_add(user):
    """Determine whether the given user has add permission.

    Parameters
    ----------
    user : str
        The kerberos of the user.

    Returns
    -------
    can_add : bool
        Whether or not the user can add projects.
    """
    if not user:
        return False
    return bool(is_sipb(user) or is_admin(user) or is_approver(user))


def is_admin(user):
    """Determine whether the given user is a project-database admin.

    Parameters
    ----------
    user : str
        The kerberos of the user.

    Returns
    -------
    is_admin : bool
        Whether or not the user is an admin.
    """
    return bool(user and user in config.ADMIN_USERS)


def is_approver(user):
    """Determine whether the given user is a project-database approver.

    Parameters
    ----------
    user : str
        The kerberos of the user.

    Returns
    -------
    is_approver : bool
        Whether or not the user is an approver.
    """
    return bool(user and user in config.APPROVER_USERS)


def can_edit(user, project_id):
    """Determine whether the given user can edit the given project.

    Parameters
    ----------
    user : str
        The kerberos of the user.
    project_id : str or int
        The project ID of the project to edit.

    Returns
    -------
    can_edit : bool
        Whether or not the user can add projects.
    """
    if not user:
        return False
    elif (
        is_admin(user)
        or is_approver(user)
        or db.get_project_creator(project_id) == user
    ):
        return True
    else:
        project_contacts = db.get_contacts(project_id)
        project_contact_emails = [contact["email"] for contact in project_contacts]
        return user + "@mit.edu" in project_contact_emails


def requires_approval(user):
    """Determine whether the given user requires approval to perform certain
    actions.

    Parameters
    ----------
    user : str
        The kerberos of the user.

    Returns
    -------
    requires_approval : bool
        Whether or not actions performed by the user require approval.
    """
    if not user:
        return True
    return not (is_admin(user) or is_approver(user) or is_keyholder(user))


def can_approve(user):
    """Determine whether the given user can approve projects.

    Parameters
    ----------
    user : str
        The kerberos of the user.

    Returns
    -------
    can_edit : bool
        Whether or not the user can approve projects.
    """
    if not user:
        return False
    return bool(is_admin(user) or is_approver(user))


def enrich_project_list_with_permissions(user, project_list):
    """Add the 'can_edit' field to each entry in the given project_list.

    Parameters
    ----------
    user : str
        The kerberos of the user.
    project_list : list of dict
        The info for each project. This will be updated in-place.

    Returns
    -------
    project_list : list of dict
        The updated project info.
    """
    user_can_approve = can_approve(user)
    for project in project_list:
        project["can_edit"] = can_edit(user, project["project_id"])
        project["can_approve"] = (
            user_can_approve and project["approval"] == "awaiting_approval"
        )
    return project_list
