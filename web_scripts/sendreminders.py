#!/usr/bin/env python

import datetime

import db
import mail

from config import EXPIRATION_BY_NUM_DAYS
EXPIRATION_HORIZON = datetime.timedelta(days=EXPIRATION_BY_NUM_DAYS)
REMIND_DAYS = set(datetime.timedelta(days=d) for d in [30, 21, 14, 7, 3, 2, 1])


def round_timedelta(in_timedelta):
    """Round a time difference to the nearest whole number of days.
    """
    if in_timedelta.days < 0:
        sign = -1
    else:
        sign = +1
    in_timedelta = abs(in_timedelta)

    fractional_part = datetime.timedelta(
        seconds=in_timedelta.seconds, microseconds=in_timedelta.microseconds
    )
    floor = datetime.timedelta(days=in_timedelta.days)
    if fractional_part >= datetime.timedelta(days=0.5):
        rounded = floor + datetime.timedelta(days=1)
    else:
        rounded = floor

    return rounded * sign


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
    """
    now = db.get_now()
    projects_needing_edits = db.get_stale_projects(
        now,
        time_horizon=EXPIRATION_HORIZON - max(REMIND_DAYS)
    )
    for project in projects_needing_edits:
        last_edit_age_rounded = round_timedelta(
            now - project['last_edit_timestamp']
        )
        if last_edit_age_rounded in REMIND_DAYS:
            mail.send_confirm_reminder_message(project,last_edit_age_rounded)

    stale_projects = db.get_stale_projects(
        now,
        time_horizon=EXPIRATION_HORIZON
    )
    for project in stale_projects:
        project['status'] = 'inactive'
        db.update_project(
            project, project['project_id'], 'projects-database-admin'
        )
        mail.send_deactivation_message(project)
    mail.send(mail.APPROVERS_LIST,mail.SERVICE_EMAIL,"Testing reminders cronjob","If you see this message, it means that cronjob for sendreminders.py ran. Please remove this test email now. Thank you.")

if __name__ == '__main__':
    main()
