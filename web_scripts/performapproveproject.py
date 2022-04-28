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
    approval_action = formutils.safe_cgi_field_get(
        arguments, 'approval_action'
    )
    approver_comments = formutils.safe_cgi_field_get(
        arguments, 'approver_comments'
    )
    approver_kerberos = authutils.get_kerberos()
    is_ok, status_messages = valutils.validate_project_id(project_id)
    if is_ok:
        is_ok, status_messages = valutils.validate_approve_project(
            project_info, project_id, approval_action, approver_comments
        )

    if is_ok:
        try:
            db.update_project(
                project_info, project_id, authutils.get_kerberos()
            )
            project_info['project_id'] = project_id
        except Exception:
            is_ok = False
            status = ''
            status += 'update_project failed with the following exception:\n'
            status += traceback.format_exc()
            status_messages = [status]

    if is_ok:
        if approval_action == 'approved':
            action = db.approve_project
            mail_action = mail.send_approve_message
            action_name = 'approve_project'
            project_info['approval'] = 'approved'
        elif approval_action == 'rejected':
            action = db.reject_project
            mail_action = mail.send_reject_message
            action_name = 'reject_project'
            project_info['approval'] = 'rejected'
        else:
            raise ValueError('Unknown approval action!')

        try:
            action(
                project_info, project_id, approver_kerberos, approver_comments
            )
        except Exception:
            is_ok = False
            status = ''
            status += '%s failed with the following exception:\n' % action_name
            status += traceback.format_exc()
            status_messages = [status]

    if approval_action == 'approved':
        title = 'Approve Project'
    elif approval_action == 'rejected':
        title = 'Reject Project'
    else:
        raise ValueError('Unknown approval action!')

    if is_ok:
        page = performutils.format_success_page(project_id, title)
        mail_action(project_info, approver_kerberos, approver_comments)
    else:
        page = performutils.format_failure_page(
            strutils.html_listify(status_messages), title
        )

    print(page)


if __name__ == '__main__':
    main()
