import authutils
import db
import strutils


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
    name_ok = len(name) >= 1
    if name_ok:
        status_messages = []
    else:
        status_messages = ['Project name must be non-empty!']
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
    # TODO: the get_project_id function does not work on the old version of
    # sqlalchemy on scripts.
    # TODO: it would be good to do a case-insensitive search
    # return db.get_project_id(name) is None
    return True, []


def validate_project_name(name):
    """Check if the project name field is valid.

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
    name_ok = True
    status_messages = []

    name_text_ok, name_msgs = validate_project_name_text(name)
    name_ok &= name_text_ok
    status_messages.extend(name_msgs)

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
    """Check if the project contact addresses are all MIT addresses.

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
    for contact in contacts:
        if not strutils.is_mit_email(contact['email']):
            is_ok = False
            status_messages.append(
                '"%s" is not an mit.edu email address!' % contact['email']
            )

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

    addresses_ok, addresses_msgs = validate_project_contact_addresses(contacts)
    is_ok &= addresses_ok
    status_messages.extend(addresses_msgs)

    return is_ok, status_messages


def validate_project_roles(roles):
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
    is_ok = True
    status_messages = []
    for role in roles:
        if (len(role['role']) == 0) or (len(role['description']) == 0):
            is_ok = False
            status_messages = ['Each role must have a name and a description!']
            break
    return is_ok, status_messages


def validate_project_info(project_info):
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

    name_ok, name_msgs = validate_project_name(project_info['name'])
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

    # TODO: this currently allows links, comm channels, and roles to be empty.
    # Do we want to require any of those at project creation time?

    return is_ok, status_messages
