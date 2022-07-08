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
    project_id = formutils.safe_cgi_field_get(arguments, 'project_id')
    revision_id = formutils.safe_cgi_field_get(arguments, 'revision_id')
    editor_kerberos = authutils.get_kerberos()
    is_ok, status_messages = valutils.validate_revision_id(
        project_id, revision_id
    )

    if is_ok:
        current_approval_status = db.get_project_approval_status(project_id)
        project_info = db.get_all_info_for_project(
            project_id, revision_id=revision_id
        )
        requires_approval = authutils.requires_approval(editor_kerberos)
        if requires_approval:
            name_changed = performutils.check_for_name_change(
                project_info, project_id
            )
            details_changed = performutils.check_for_info_change(
                project_info, project_id
            )

        try:
            db.rollback_project(project_id, revision_id, editor_kerberos)
        except Exception:
            is_ok = False
            status = ''
            status += 'rollback_project failed with the following exception:\n'
            status += traceback.format_exc()
            status_messages = [status]

    if is_ok:
        if (
            (project_info['approval_status'] == 'awaiting_approval') and
            (current_approval_status != 'awaiting_approval')
        ):
            # When rollback turns an approved or rejected project into one
            # which is awaiting approval, email the approvers:
            mail.send_to_approvers(project_info)
            message = (
                'This rollback has changed the approval status to '
                '"awaiting approval." The details have been sent to the '
                'moderators for approval. You will be notified once the '
                'posting has been reviewed.'
            )
        elif (
            (project_info['approval_status'] == 'approved') and
            requires_approval
        ):
            if name_changed:
                # When a rollback initiated by a non-approver changes the name
                # and results in an approved project, change status to
                # "awaiting_approval" and email the approvers:
                db.set_project_status_to_awaiting_approval(
                    project_info, project_id, editor_kerberos
                )
                mail.send_to_approvers(project_info)
                message = (
                    'This rollback has changed the project\'s name. The '
                    'updated project details have been sent to the '
                    'moderators for approval. You will be notified once the '
                    'posting has been reviewed.'
                )
            elif details_changed:
                # When a non-approver initiates a rollback which changes the
                # project details, send a notification email to the approvers,
                # but do not change the project status:
                mail.send_edit_notice_to_approvers(
                    project_info, editor_kerberos
                )
                message = None
            else:
                message = None
        else:
            message = None

        page = performutils.format_success_page(
            project_id, 'Roll Back Project', message=message
        )
    else:
        page = performutils.format_failure_page(
            strutils.html_listify(status_messages), 'Roll Back Project'
        )

    print(page)


if __name__ == '__main__':
    main()
