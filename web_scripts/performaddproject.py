#!/usr/bin/env python
# -*- coding: utf-8 -*-

import traceback

import cgi

import authutils
import db
import formutils
import mail
import performutils
import strutils
import valutils

# TODO: May want to turn error listing off once stable?
import cgitb
cgitb.enable()


def main():
    """Respond to an add project request, displaying the appropriate status
    message.
    """
    arguments = cgi.FieldStorage()
    project_info = formutils.args_to_dict(arguments)
    is_ok, status_messages = valutils.validate_add_project(project_info)

    if is_ok:
        requestor_kerberos = authutils.get_kerberos()
        can_approve = authutils.can_approve(requestor_kerberos)
        initial_approval = 'approved' if can_approve else 'awaiting_approval'
        try:
            project_id = db.add_project(
                project_info,
                authutils.get_kerberos(),
                initial_approval=initial_approval
            )
            assert project_id != -1
            project_info['project_id'] = project_id
        except Exception:
            is_ok = False
            status = ''
            status += 'add_project failed with the following exception:\n'
            status += traceback.format_exc()
            status_messages = [status]

    if is_ok:
        if can_approve:
            message = None
        else:
            message = (
                'The following project details have been sent to the '
                'moderators for approval. You will be notified once the '
                'posting has been reviewed.'
            )
            mail.send_to_approvers(project_info)

        page = performutils.format_success_page(
            project_id, 'Add Project', message=message
        )
    else:
        page = performutils.format_failure_page(
            strutils.html_listify(status_messages), 'Add Project'
        )

    print(page)


if __name__ == '__main__':
    main()
