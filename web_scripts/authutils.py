# Based on:
# https://github.com/sipb/hwops/blob/master/web_scripts/kerbparse.py
# https://github.com/sipb/hwops/blob/master/web_scripts/main.py
# https://github.com/sipb/hwops/blob/master/web_scripts/moira.py

import os

import db
import roster
import config


def get_kerberos():
    """Get the kerberos of the user. Returns None if there is no user.

    Returns
    -------
    kerberos : str
        The kerberos (username only) for the user.
    """
    email = get_email()
    if email:
        return email[:email.index('@')]
    else:
        return None


def get_email():
    """Get the email of the user. Returns None if there is no user.

    Returns
    -------
    email : str
        The email for the user.
    """
    email = os.getenv('SSL_CLIENT_S_DN_Email')
    if (
        (email is None) or
        (not email.lower().endswith('@mit.edu')) or
        (email.count('@') != 1)
    ):
        return None
    else:
        return email


def get_base_url(do_authenticate):
    """Get the base URL.

    Parameters
    ----------
    do_authenticate : bool
        Whether or not to add port 444 to trigger authentication.

    Returns
    -------
    url : str
        The base URL.
    """
    host = os.environ['HTTP_HOST'].split(':')[0]
    if do_authenticate:
        return 'https://%s:444' % host
    else:
        return 'https://%s' % host


def get_auth_url(do_authenticate):
    """Get the authentication URL.

    Parameters
    ----------
    do_authenticate : bool
        Whether or not to add port 444 to trigger authentication.

    Returns
    -------
    url : str
        The authentication URL.
    """
    return get_base_url(do_authenticate) + os.environ['REQUEST_URI']


def is_sipb(user):
    if user:
        return user in roster.sipb_roster
    else:
        return False


def is_keyholder(user):
    # NOTE: the roster uses the older "prospective" vs. "member" distinction,
    # rather than "member" vs. "keyholder".
    if user:
        return roster.sipb_roster.get(user, 'other') == 'member'
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
    elif is_sipb(user) or is_admin(user) or is_approver(user):
        return True
    else:
        return False


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
    if user and user in config.ADMIN_USERS:
        return True
    else:
        return False


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
    if user and user in config.APPROVER_USERS:
        return True
    else:
        return False


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
    elif is_admin(user):
        return True
    elif is_approver(user):
        return True
    elif db.get_project_creator(project_id) == user:
        return True
    else:
        project_contacts = db.get_contacts(project_id)
        project_contact_emails = [
            contact['email'] for contact in project_contacts
        ]
        if user + '@mit.edu' in project_contact_emails:
            return True
        else:
            return False


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
    elif is_admin(user) or is_approver(user) or is_keyholder(user):
        return False
    else:
        return True


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
    elif is_admin(user):
        return True
    elif is_approver(user):
        return True
    else:
        return False


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
        project['can_edit'] = can_edit(user, project['project_id'])
        project['can_approve'] = (
            user_can_approve and
            project['approval'] == 'awaiting_approval'
        )
    return project_list
