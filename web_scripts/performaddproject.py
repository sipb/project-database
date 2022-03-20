#!/usr/bin/env python
# -*- coding: utf-8 -*-

import traceback

import cgi
import jinja2

import authutils
import db
import strutils

# TODO: May want to turn error listing off once stable?
import cgitb
cgitb.enable()


def contact_list_to_dict_list(contact_list):
    """Convert a list of contacts to a properly-formatted list of dicts.

    The first entry is assumed to be the primary contact.

    Parameters
    ----------
    contact_list : list of str
        The email addresses for each contact.

    Returns
    -------
    contact_dict_list : list of dict
        The formatted contact dicts with types assigned.
    """
    result = [
        {'email': contact, 'type': 'secondary'}
        for contact in contact_list
        if len(contact) > 0
    ]
    if len(result) > 0:
        result[0]['type'] = 'primary'
    return result


def get_role_ids(arguments):
    """Get all role IDs from the arguments from CGI.

    Parameters
    ----------
    arguments : cgi.FieldStorage
        The data from the form.

    Returns
    -------
    role_ids : list of str
        The role IDs present in the arguments, in the order they are discovered
        in.
    """
    role_ids = set()
    for key in arguments.keys():
        # Check all fields so that we can catch mal-formed inputs:
        if key.startswith('role_name_'):
            role_ids.add(key[len('role_name_'):])
        elif key.startswith('role_description_'):
            role_ids.add(key[len('role_description_'):])
        elif key.startswith('role_prereqs_'):
            role_ids.add(key[len('role_prereqs_'):])
    return list(role_ids)


def safe_cgi_field_get(arguments, field, default=''):
    """Get a field from CGI arguments, with failback for absent fields.

    Parameters
    ----------
    arguments : cgi.FieldStorage
        The data from the form.
    field : str
        The field to get.
    default : str, optional
        The value to use when a field is not present. Default is the empty
        string.

    Returns
    -------
    value : str
        The field value.
    """
    return arguments[field].value if field in arguments else default


def extract_roles(arguments):
    """Extract the role dicts from the arguments from CGI.

    Parameters
    ----------
    arguments : cgi.FieldStorage
        The data from the form.

    Returns
    -------
    roles : list of dict
        The information for each role.
    """
    role_ids = get_role_ids(arguments)
    roles = []
    for role_id in role_ids:
        roles.append(
            {
                'role': safe_cgi_field_get(arguments, 'role_name_' + role_id),
                'description': safe_cgi_field_get(
                    arguments, 'role_description_' + role_id
                ),
                'prereq': safe_cgi_field_get(
                    arguments, 'role_prereqs_' + role_id
                )
            }
        )
        if len(roles[-1]['prereq']) == 0:
            roles[-1]['prereq'] = None
    return roles


def args_to_dict(arguments):
    """Reformat the arguments from CGI into a dict.

    Parameters
    ----------
    arguments : cgi.FieldStorage
        The data from the form.

    Returns
    -------
    project_info : dict
        The project info dict.
    """
    return {
        'name': safe_cgi_field_get(arguments, 'name'),
        'description': safe_cgi_field_get(arguments, 'description'),
        'status': safe_cgi_field_get(arguments, 'status'),
        'links': [
            strutils.make_url_absolute(link)
            for link in strutils.split_comma_sep(
                safe_cgi_field_get(arguments, 'links')
            )
        ],
        'comm_channels': strutils.split_comma_sep(
            safe_cgi_field_get(arguments, 'comm_channels')
        ),
        'contacts': contact_list_to_dict_list(
            strutils.split_comma_sep(safe_cgi_field_get(arguments, 'contacts'))
        ),
        'roles': extract_roles(arguments)
    }


def validate_add_permission():
    """Check if the user has permission to add projects.
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
    """
    name_ok = len(name) >= 1
    if name_ok:
        status_messages = []
    else:
        status_messages = ['Project name must be non-empty!']
    return name_ok, status_messages


def validate_project_name_available(name):
    """Check if the project name is available.
    """
    # TODO: the get_project_id function does not work on the old version of
    # sqlalchemy on scripts.
    # TODO: it would be good to do a case-insensitive search
    # return db.get_project_id(name) is None
    return True, []


def validate_project_name(name):
    """Check if the project name field is valid.
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
    """
    description_ok = len(description) >= 1
    if description_ok:
        status_messages = []
    else:
        status_messages = ['Project description must be non-empty!']
    return description_ok, status_messages


def validate_project_contacts_nonempty(contacts):
    """Check if there is at least one contact.
    """
    is_ok = len(contacts) >= 1
    if is_ok:
        status_messages = []
    else:
        status_messages = ['There must be at least one contact!']
    return is_ok, status_messages


def validate_project_contact_addresses(contacts):
    """Check if the project contact addresses are all MIT addresses.
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
    """
    is_ok = True
    status_messages = []
    for role in roles:
        if (len(role['role']) == 0) or (len(role['description']) == 0):
            is_ok = False
            status_messages = ['Each role must have a name and a description!']
            break
    return is_ok, status_messages


def validate(project_info):
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
    status : str
        A status message indicating the result of the validation.
    is_ok : bool
        Indicates whether or not the project is OK to add.
    """
    is_ok = True
    defect_list = []

    permission_ok, permission_msgs = validate_add_permission()
    is_ok &= permission_ok
    defect_list.extend(permission_msgs)

    name_ok, name_msgs = validate_project_name(project_info['name'])
    is_ok &= name_ok
    defect_list.extend(name_msgs)

    description_ok, description_msgs = validate_project_description(
        project_info['description']
    )
    is_ok &= description_ok
    defect_list.extend(description_msgs)

    contacts_ok, contacts_msgs = validate_project_contacts(
        project_info['contacts']
    )
    is_ok &= contacts_ok
    defect_list.extend(contacts_msgs)

    roles_ok, roles_msgs = validate_project_roles(project_info['roles'])
    is_ok &= roles_ok
    defect_list.extend(roles_msgs)

    # TODO: this currently allows links, comm channels, and roles to be empty.
    # Do we want to require any of those at project creation time?

    if is_ok:
        return 'Success!', True
    else:
        return strutils.html_listify(defect_list), False


def add_project(project_info):
    """Add the given project to the database.

    Parameters
    ----------
    project_info : dict
        The project info extracted from the form.

    Returns
    -------
    project_id : int
        The project_id (primary key) for the newly-added project.
    """
    # TODO: this needs to be implemented!
    return -1


def format_success_page(project_info):
    """Format the success page.

    Parameters
    ----------
    project_info : dict
        The project info which was added to the database.

    Returns
    -------
    result : str
        The HTML to display.
    """
    jenv = jinja2.Environment(
        loader=jinja2.FileSystemLoader('templates'),
        autoescape=True
    )
    result = ''
    result += 'Content-type: text/html\n\n'
    result += jenv.get_template('performaddprojectsuccess.html').render(
        project=project_info
    ).encode('utf-8')
    return result


def format_failure_page(status):
    """Format the failure page.

    Parameters
    ----------
    status : str
        The status string explaining why the project was rejected.

    Returns
    -------
    result : str
        The HTML to display.
    """
    jenv = jinja2.Environment(
        loader=jinja2.FileSystemLoader('templates'),
        autoescape=True
    )
    result = ''
    result += 'Content-type: text/html\n\n'
    result += jenv.get_template('performaddprojectfailure.html').render(
        status=status
    ).encode('utf-8')
    return result


def main():
    """Respond to an add project request, displaying the appropriate status
    message.
    """
    arguments = cgi.FieldStorage()
    project_info = args_to_dict(arguments)
    status, is_ok = validate(project_info)

    if is_ok:
        try:
            project_id = add_project(project_info)
            project_info['project_id'] = project_id
        except Exception:
            is_ok = False
            status = ''
            status += 'add_project failed with the following exception:\n'
            status += traceback.format_exc()
            status += '\n'
            status = cgi.escape(status, quote=True)
            status = status.replace('\n', '<br>')

    if is_ok:
        page = format_success_page(project_info)
    else:
        page = format_failure_page(status)

    print(page)


if __name__ == '__main__':
    main()
