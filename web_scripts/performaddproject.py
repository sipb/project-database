#!/usr/bin/env python
# -*- coding: utf-8 -*-

import traceback

import cgi
import jinja2

import formutils
import strutils
import valutils

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
                'role': formutils.safe_cgi_field_get(
                    arguments, 'role_name_' + role_id
                ),
                'description': formutils.safe_cgi_field_get(
                    arguments, 'role_description_' + role_id
                ),
                'prereq': formutils.safe_cgi_field_get(
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
        'name': formutils.safe_cgi_field_get(arguments, 'name'),
        'description': formutils.safe_cgi_field_get(arguments, 'description'),
        'status': formutils.safe_cgi_field_get(arguments, 'status'),
        'links': [
            strutils.make_url_absolute(link)
            for link in strutils.split_comma_sep(
                formutils.safe_cgi_field_get(arguments, 'links')
            )
        ],
        'comm_channels': strutils.split_comma_sep(
            formutils.safe_cgi_field_get(arguments, 'comm_channels')
        ),
        'contacts': contact_list_to_dict_list(
            strutils.split_comma_sep(
                formutils.safe_cgi_field_get(arguments, 'contacts')
            )
        ),
        'roles': extract_roles(arguments)
    }


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
    project_info = strutils.obfuscate_project_info_dicts([project_info])[0]
    project_info = strutils.make_project_info_dicts_links_absolute(
        [project_info]
    )[0]
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
    is_ok, status_messages = valutils.validate_project_info(project_info)

    if is_ok:
        try:
            project_id = add_project(project_info)
            project_info['project_id'] = project_id
        except Exception:
            is_ok = False
            status = ''
            status += 'add_project failed with the following exception:\n'
            status += traceback.format_exc()
            status_messages = [status]

    if is_ok:
        page = format_success_page(project_info)
    else:
        page = format_failure_page(strutils.html_listify(status_messages))

    print(page)


if __name__ == '__main__':
    main()
