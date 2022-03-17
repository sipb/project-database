#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
import jinja2

import strutils


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
        {'email': contact, 'type': 'secondary'} for contact in contact_list
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
    role_ids = []
    for key in arguments.keys():
        if key.startswith('role_name_'):
            role_ids.append(key[len('role_name_'):])
    return role_ids


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
                'role': arguments['role_name_' + role_id].value,
                'description': arguments['role_description_' + role_id].value,
                'prereq': arguments['role_prereqs_' + role_id].value
            }
        )
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
        'name': arguments['name'].value,
        'description': arguments['description'].value,
        'status': arguments['status'].value,
        'links': strutils.split_comma_sep(arguments['links'].value),
        'comm_channels': strutils.split_comma_sep(
            arguments['comm_channels'].value
        ),
        'contacts': contact_list_to_dict_list(
            strutils.split_comma_sep(arguments['contacts'].value)
        ),
        'roles': extract_roles(arguments)
    }


def add_project(arguments):
    """Add the given project 
    """
    # TODO: This should authenticate the user, do any sort of validation/
    # sanitization we need, and write to the DB. It should return an error
    # message if it fails, which we should check and use to render the
    # appropriate follow-on page.
    pass


def render_result_page(project_info):
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


def main():
    arguments = cgi.FieldStorage()
    project_info = args_to_dict(arguments)
    add_project(project_info)
    page = render_result_page(project_info)
    print(page)


if __name__ == '__main__':
    main()
