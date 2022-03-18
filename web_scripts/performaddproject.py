#!/usr/bin/env python
# -*- coding: utf-8 -*-

import traceback

import cgi
import jinja2

import authutils
import db
import strutils

# TODO: May want to turn error help off once stable?
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
        'links': strutils.split_comma_sep(
            safe_cgi_field_get(arguments, 'links')
        ),
        'comm_channels': strutils.split_comma_sep(
            safe_cgi_field_get(arguments, 'comm_channels')
        ),
        'contacts': contact_list_to_dict_list(
            strutils.split_comma_sep(safe_cgi_field_get(arguments, 'contacts'))
        ),
        'roles': extract_roles(arguments)
    }


def validate_add_permission():
    user = authutils.get_kerberos()
    can_add = authutils.can_add(user)
    return can_add


def validate_project_name(name):
    return len(name) >= 1


def validate_project_name_available(name):
    # TODO: the get_project_id function does not work on the old version of
    # sqlalchemy on scripts.
    # TODO: it would be good to do a case-insensitive search
    # return db.get_project_id(name) is None
    return True


def validate_project_description(description):
    return len(description) >= 1


def validate_project_contacts(contacts):
    return len(contacts) >= 1


def validate_project_contact_addresses(contacts):
    for contact in contacts:
        if not strutils.is_mit_email(contact['email']):
            return False
    return True


def validate_project_roles(roles):
    for role in roles:
        if (len(role['role']) == 0) or (len(role['description']) == 0):
            return False
    return True


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
    defect_list = []

    if not validate_add_permission():
        defect_list.append('User is not authorized to add projects!')

    if not validate_project_name(project_info['name']):
        defect_list.append('Project name must be non-empty!')

    if not validate_project_name_available(project_info['name']):
        defect_list.append('A project with that name already exists!')

    if not validate_project_description(project_info['description']):
        defect_list.append('Project description must be non-empty!')

    if not validate_project_contacts(project_info['contacts']):
        defect_list.append('There must be at least one contact!')

    if not validate_project_contact_addresses(project_info['contacts']):
        defect_list.append('Contacts must be mit.edu email addresses!')

    if not validate_project_roles(project_info['roles']):
        defect_list.append('Each role must have a name and a description!')

    # TODO: this currently allows links, comm channels, and roles to be empty.
    # Do we want to require any of those at project creation time?

    if len(defect_list) == 0:
        return 'Success!', True
    else:
        return strutils.html_listify(defect_list), False


def add_project(project_info):
    """Add the given project to the database.

    Parameters
    ----------
    project_info : dict
        The project info extracted from the form.
    """
    pass


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
            add_project(project_info)
        except Exception:
            is_ok = False
            status = ''
            status += 'add_project failed with the following exception:\n'
            status += traceback.format_exc()
            status += '\n'
            status = cgi.escape(status, quote=True)
            status = status.replace('\n', '<br>')

    if is_ok:
        add_project(project_info)
        page = format_success_page(project_info)
    else:
        page = format_failure_page(status)

    print(page)


if __name__ == '__main__':
    main()
