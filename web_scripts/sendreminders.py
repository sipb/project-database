#!/usr/bin/env python

import datetime

import db
import mail


def main():
    """The sendreminders script does two things:
        * For projects which are close to stale, send an email to the
            contact(s) with a link to the confirm page.
        * For projects which are stale, set the project status to "inactive"
            and send an email to the contact(s) notifying them that their
            project has been deactivated. This message will also contain an
            edit link, and a reminder that they should change the status back
            to active if they want their project to appear in the list of
            active projects.

    Note that these actions are performed EVERY time the script is run. If we
    run the script daily, this might lead to lots of spam. We could consider
    running it weekly to cut down on this, while still getting the point across
    that people should update their projects.
    """
    projects_needing_edits = db.get_stale_projects(
        time_horizon=datetime.timedelta(days=335)
    )
    for project in projects_needing_edits:
        mail.send_confirm_reminder_message(project)

    stale_projects = db.get_stale_projects(
        time_horizon=datetime.timedelta(days=365)
    )
    for project in stale_projects:
        project['status'] = 'inactive'
        db.update_project(
            project, project['project_id'], 'projects-database-admin'
        )
        mail.send_deactivation_message(project)


if __name__ == '__main__':
    main()
