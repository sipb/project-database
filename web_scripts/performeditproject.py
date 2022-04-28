#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
import traceback

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
    arguments = cgi.FieldStorage()
    project_info = formutils.args_to_dict(arguments)
    project_id = formutils.safe_cgi_field_get(arguments, 'project_id')
    editor_kerberos = authutils.get_kerberos()
    is_ok, status_messages = valutils.validate_project_id(project_id)
    if is_ok:
        is_ok, status_messages = valutils.validate_edit_project(
            project_info, project_id
        )

    if is_ok:
        try:
            db.update_project(project_info, project_id, editor_kerberos)
            project_info['project_id'] = project_id
        except Exception:
            is_ok = False
            status = ''
            status += 'update_project failed with the following exception:\n'
            status += traceback.format_exc()
            status_messages = [status]

    if is_ok:
        page = performutils.format_success_page(project_id, 'Edit Project')

        # When updating a rejected project, change status to
        # "awaiting_approval" and email the approvers:
        if db.get_project_approval_status(project_id) == 'rejected':
            db.unreject_project(project_info, project_id, editor_kerberos)
            mail.send_to_approvers(project_info)
    else:
        page = performutils.format_failure_page(
            strutils.html_listify(status_messages), 'Edit Project'
        )

    print(page)


if __name__ == '__main__':
    main()
