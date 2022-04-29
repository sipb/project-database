import authutils
import db
import schema
import strutils

# This module contains functions to validate data. Any function starting with
# "validate_" shall return a bool (with True indicating that the condition is
# satisfied) and a list of str containing any error messages. The list shall be
# empty if the bool is True and shall have one or more entries if the bool is
# False. This interface does not define the input arguments, as these vary
# depending on what is to be validated.
#
# Functions which do NOT start with "validate_" are helper functions, and do
# not need to adhere to the interface defined above.


def all_unique(vals, ignore_case=True):
    """Check if all entries in a list are unique.

    Parameters
    ----------
    vals : list of str
        The values
    ignore_case : bool, optional
        Whether or not to ignore case. Default is True.

    Returns
    -------
    result : bool
        Whether or not all of the values in vals are unique.
    """
    if ignore_case:
        vals = [val.lower() for val in vals]
    return len(set(vals)) == len(vals)


def validate_add_permission():
    """Check if the user has permission to add projects.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    user = authutils.get_kerberos()
    can_add = authutils.can_add(user)
    if can_add:
        status_messages = []
    else:
        status_messages = ['User is not authorized to add projects!']
    return can_add, status_messages


def validate_project_name_text(name):
    """Check if the project name text is valid.

    Parameters
    ----------
    name : str
        The proposed project name.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    max_len = schema.Projects.__table__.columns['name'].type.length
    if len(name) < 1:
        name_ok = False
        status_messages = ['Project name must be non-empty!']
    elif len(name) > max_len:
        name_ok = False
        status_messages = [
            'Project name must be less than %d characters!' % max_len
        ]
    else:
        name_ok = True
        status_messages = []

    return name_ok, status_messages


def validate_project_name_available(name):
    """Check if the project name is available.

    Parameters
    ----------
    name : str
        The proposed project name.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    project_id = db.get_project_id(name)
    if project_id:
        return False, ['A project with name "%s" already exists!' % name]
    else:
        return True, []


def validate_project_name(name, previous_name=None):
    """Check if the project name field is valid.

    Parameters
    ----------
    name : str
        The proposed project name.
    previous_name : str, optional
        The previous name of the project (if this is an edit and not an add).

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    name_ok = True
    status_messages = []

    name_text_ok, name_msgs = validate_project_name_text(name)
    name_ok &= name_text_ok
    status_messages.extend(name_msgs)

    if (previous_name is None) or (name.lower() != previous_name.lower()):
        name_available, name_msgs = validate_project_name_available(name)
        name_ok &= name_available
        status_messages.extend(name_msgs)

    return name_ok, status_messages


def validate_project_description(description):
    """Check if the project description is non-empty.

    Parameters
    ----------
    description : str
        The project description.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    description_ok = len(description.split()) >= 3
    if description_ok:
        status_messages = []
    else:
        status_messages = [
            'Project description must have at least three words!'
        ]
    return description_ok, status_messages


def validate_project_contacts_nonempty(contacts):
    """Check if there is at least one contact.

    Parameters
    ----------
    contacts : list of dict
        The list of contacts.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    is_ok = len(contacts) >= 1
    if is_ok:
        status_messages = []
    else:
        status_messages = ['There must be at least one contact!']
    return is_ok, status_messages


def validate_project_contact_addresses(contacts):
    """Check if the project contact addresses are all MIT addresses, and at
    least one is of the form <username>@mit.edu.

    Parameters
    ----------
    contacts : list of dict
        The list of contacts. Must be non-empty.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    max_len = schema.ContactEmails.__table__.columns['email'].type.length

    is_ok = True
    status_messages = []

    contains_plain_mit = False
    for contact in contacts:
        if not strutils.is_mit_email(contact['email']):
            is_ok = False
            status_messages.append(
                '"%s" is not an mit.edu email address!' % contact['email']
            )

        if len(contact['email']) > max_len:
            is_ok = False
            status_messages.append(
                '"%s" is too long (%d character limit)!' % (
                    contact['email'], max_len
                )
            )

        if strutils.is_plain_mit_email(contact['email']):
            contains_plain_mit = True

    if not contains_plain_mit:
        is_ok = False
        status_messages.append(
            'At least one contact must have an email address of the form '
            '"<username>@mit.edu" (otherwise no contacts will be able to edit '
            'project info).'
        )

    return is_ok, status_messages


def validate_project_contacts_unique(contacts):
    """Check if the project contact addresses are all unique.

    Parameters
    ----------
    contacts : list of dict
        The list of contacts.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    is_ok = all_unique([contact['email'] for contact in contacts])
    if is_ok:
        status_messages = []
    else:
        status_messages = ['Contact emails must be unique.']

    return is_ok, status_messages


def validate_project_contacts(contacts):
    """Check if the project contacts field is valid.

    Parameters
    ----------
    contacts : list of dict
        The list of contacts.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    is_ok = True
    status_messages = []

    is_nonempty, nonempty_msgs = validate_project_contacts_nonempty(contacts)
    is_ok &= is_nonempty
    status_messages.extend(nonempty_msgs)

    if is_nonempty:
        addresses_ok, addresses_msgs = validate_project_contact_addresses(
            contacts
        )
        is_ok &= addresses_ok
        status_messages.extend(addresses_msgs)

        unique_ok, unique_msgs = validate_project_contacts_unique(contacts)
        is_ok &= unique_ok
        status_messages.extend(unique_msgs)

    return is_ok, status_messages


def validate_project_role_fields(roles):
    """Check if the project roles all have names and descriptions.

    Parameters
    ----------
    roles : list of dict
        The list of roles.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    max_len = schema.Roles.__table__.columns['role'].type.length

    is_ok = True
    status_messages = []
    for role in roles:
        if (len(role['role']) == 0) or (len(role['description']) == 0):
            is_ok = False
            status_messages = ['Each role must have a name and a description!']
            break

        if len(role['role']) > max_len:
            is_ok = False
            status_messages = [
                'Role names can be no longer than %d characters!' % max_len
            ]
            break
    return is_ok, status_messages


def validate_project_roles_unique(roles):
    """Check if the project role names are all unique.

    Parameters
    ----------
    roles : list of dict
        The list of roles.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    is_ok = all_unique([role['role'] for role in roles])
    if is_ok:
        status_messages = []
    else:
        status_messages = ['Role names must be unique.']

    return is_ok, status_messages


def validate_project_roles(roles):
    """Check if the project roles are valid.

    Parameters
    ----------
    roles : list of dict
        The list of roles.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    is_ok = True
    status_messages = []

    fields_ok, fields_msgs = validate_project_role_fields(roles)
    is_ok &= fields_ok
    status_messages.extend(fields_msgs)

    unique_ok, unique_msgs = validate_project_roles_unique(roles)
    is_ok &= unique_ok
    status_messages.extend(unique_msgs)

    return is_ok, status_messages


def validate_project_links(links):
    """Check if the project links are all unique.

    Parameters
    ----------
    links : list of dict
        The list of links.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    is_ok = all_unique([link['link'] for link in links])
    if is_ok:
        status_messages = []
    else:
        status_messages = ['Links must be unique.']

    return is_ok, status_messages


def validate_project_comm_channels(comm_channels):
    """Check if the project comm channels are all unique.

    Parameters
    ----------
    comm_channels : list of dict
        The list of comm channels.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    is_ok = all_unique(
        [comm_channel['commchannel'] for comm_channel in comm_channels]
    )
    if is_ok:
        status_messages = []
    else:
        status_messages = ['Comm channels must be unique.']

    return is_ok, status_messages


def validate_project_info(project_info, previous_name=None):
    """Validate that the given project info is OK.

    Parameters
    ----------
    project_info : dict
        The project info extracted from the form.
    previous_name : str, optional
        The previous name of the project (if this is an edit and not an add).

    Returns
    -------
    is_ok : bool
        Indicates whether or not the project info is OK.
    status_messages : list of str
        A list of status messages indicating the result of the validation.
    """
    is_ok = True
    status_messages = []

    name_ok, name_msgs = validate_project_name(
        project_info['name'], previous_name=previous_name
    )
    is_ok &= name_ok
    status_messages.extend(name_msgs)

    description_ok, description_msgs = validate_project_description(
        project_info['description']
    )
    is_ok &= description_ok
    status_messages.extend(description_msgs)

    contacts_ok, contacts_msgs = validate_project_contacts(
        project_info['contacts']
    )
    is_ok &= contacts_ok
    status_messages.extend(contacts_msgs)

    roles_ok, roles_msgs = validate_project_roles(project_info['roles'])
    is_ok &= roles_ok
    status_messages.extend(roles_msgs)

    links_ok, links_msgs = validate_project_links(project_info['links'])
    is_ok &= links_ok
    status_messages.extend(links_msgs)

    comms_ok, comms_msgs = validate_project_comm_channels(
        project_info['comm_channels']
    )
    is_ok &= comms_ok
    status_messages.extend(comms_msgs)

    # TODO: this currently allows links, comm channels, and roles to be empty.
    # Do we want to require any of those at project creation time?

    return is_ok, status_messages


def validate_add_project(project_info):
    """Validate that the given project is OK to add.

    In particular, check that:
    * The user is signed-in and is authorized to add projects.
    * The project_info is properly-formed.

    Parameters
    ----------
    project_info : dict
        The project info extracted from the form.

    Returns
    -------
    is_ok : bool
        Indicates whether or not the project is OK to add.
    status_messages : list of str
        A list of status messages indicating the result of the validation.
    """
    is_ok = True
    status_messages = []

    permission_ok, permission_msgs = validate_add_permission()
    is_ok &= permission_ok
    status_messages.extend(permission_msgs)

    info_ok, info_msgs = validate_project_info(project_info)
    is_ok &= info_ok
    status_messages.extend(info_msgs)

    return is_ok, status_messages


def validate_edit_permission(project_id):
    """Validate that the user has permission to edit the project.

    Parameters
    ----------
    project_id : str or int
        The project ID.

    Returns
    -------
    is_ok : bool
        Indicates whether or not the project is OK to edit.
    status_messages : list of str
        A list of status messages indicating the result of the validation.
    """
    user = authutils.get_kerberos()
    can_edit = authutils.can_edit(user, project_id)
    if can_edit:
        return True, []
    else:
        return False, ['User is not authorized to edit this project!']


def validate_edit_project(project_info, project_id):
    """Validate that the given project is OK to edit.

    In particular, check that:
    * The user is signed-in and is authorized to edit the project.
    * The project_info is properly-formed.

    Parameters
    ----------
    project_info : dict
        The project info extracted from the form.
    project_id : int
        The ID of the project to edit.

    Returns
    -------
    is_ok : bool
        Indicates whether or not the project is OK to edit.
    status_messages : list of str
        A list of status messages indicating the result of the validation.
    """
    is_ok = True
    status_messages = []

    permission_ok, permission_msgs = validate_edit_permission(project_id)
    is_ok &= permission_ok
    status_messages.extend(permission_msgs)

    previous_name = db.get_project_name(project_id)
    info_ok, info_msgs = validate_project_info(
        project_info, previous_name=previous_name
    )
    is_ok &= info_ok
    status_messages.extend(info_msgs)

    return is_ok, status_messages


def validate_approval_permission():
    """Check if the user has permission to approve projects.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    user = authutils.get_kerberos()
    is_ok = authutils.can_approve(user)
    if is_ok:
        status_messages = []
    else:
        status_messages = ['User is not authorized to approve projects!']
    return is_ok, status_messages


def validate_approval_action(approval_action):
    """Check if the selected approval action is valid.

    Parameters
    ----------
    approval_action : str
        The selected approval action.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    is_ok = approval_action in ['approved', 'rejected']
    if is_ok:
        status_messages = []
    else:
        status_messages = [
            '"%s" is not a valid approval action!' % approval_action
        ]
    return is_ok, status_messages


def validate_approval_comments(approval_action, approver_comments):
    """Check if the approver comments are valid.

    Parameters
    ----------
    approval_action : str
        The selected approval action.
    approver_comments : str
        The reviewer's comments.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    if approval_action == 'rejected':
        is_ok = len(approver_comments.split()) >= 3
    else:
        is_ok = True

    if is_ok:
        status_messages = []
    else:
        status_messages = [
            'Comments must have at least three words when rejecting a project!'
        ]

    return is_ok, status_messages


def validate_approve_project(
    project_info, project_id, approval_action, approver_comments
):
    """Validate that the given project is OK to approve/reject, possibly
    including changes to the project info made by the reviewer.

    In particular, check that:
    * The user is signed-in and is authorized to approve projects.
    * The project_info is properly-formed.
    * If the project is to be rejected, comments have been provided.

    Parameters
    ----------
    project_info : dict
        The project info extracted from the form.
    project_id : int
        The ID of the project to edit.

    Returns
    -------
    is_ok : bool
        Indicates whether or not the project is OK to edit.
    status_messages : list of str
        A list of status messages indicating the result of the validation.
    """
    is_ok = True
    status_messages = []

    permission_ok, permission_msgs = validate_approval_permission()
    is_ok &= permission_ok
    status_messages.extend(permission_msgs)

    previous_name = db.get_project_name(project_id)
    info_ok, info_msgs = validate_project_info(
        project_info, previous_name=previous_name
    )
    is_ok &= info_ok
    status_messages.extend(info_msgs)

    action_ok, action_msgs = validate_approval_action(approval_action)

    comments_ok, comments_msgs = validate_approval_comments(
        approval_action, approver_comments
    )
    is_ok &= comments_ok
    status_messages.extend(comments_msgs)

    return is_ok, status_messages


def validate_project_id_is_int(project_id):
    """Check if the given project ID is interpretable as an int.

    Parameters
    ----------
    project_id : str
        The project ID to check. Assumed to be a string coming from a CGI form.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    try:
        project_id = int(project_id)
    except ValueError:
        return False, ['"%s" is not a valid project ID!' % project_id]
    else:
        return True, []


def validate_project_id_exists(project_id):
    """Check if the given project ID exists (and hence can be edited).

    Parameters
    ----------
    project_id : str
        The project ID to check. Assumed to be a string coming from a CGI form.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    project_id = int(project_id)
    project_info = db.get_project(project_id)
    if len(project_info) == 0:
        is_ok = False
        status_messages = ['There is no project with id "%d"!' % project_id]
    elif len(project_info) == 1:
        is_ok = True
        status_messages = []
    else:
        is_ok = False
        status_messages = [
            'There are %d projects with id "%d"!' % (
                len(project_info), project_id
            )
        ]

    return is_ok, status_messages


def validate_project_id(project_id):
    """Check if the given project ID is OK to edit.

    Parameters
    ----------
    project_id : str
        The project ID to check. Assumed to be a string coming from a CGI form.

    Returns
    -------
    is_ok : bool
        Whether or not the validation was passed.
    status_messages : list of str
        A list of status messages.
    """
    is_ok = True
    status_messages = []

    is_int, is_int_status = validate_project_id_is_int(project_id)
    is_ok &= is_int
    status_messages.extend(is_int_status)

    if is_int:
        is_project, is_project_status = validate_project_id_exists(project_id)
        is_ok &= is_project
        status_messages.extend(is_project_status)

    return is_ok, status_messages 
