import smtplib
from email.mime.text import MIMEText

import db


def send(recipient, sender, subject, message):
    msg = MIMEText(message)

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    s = smtplib.SMTP('outgoing.mit.edu', 25)
    s.sendmail(sender, [recipient], msg.as_string())
    s.quit()


def send_to_approvers(project_info):
    """Send a message to the approver mailing list notifying that a project is
    ready for review.
    """
    # TODO: Not implemented yet!
    pass


def send_approve_message(project_info, approver_kerberos, approver_comments):
    """Send a message to the project creator and points of contact indicating
    that the project has been accepted.
    """
    # TODO: Not implemented yet!

    # Get point of contacts
    point_of_contacts = [db.get_project_creator(project_info['project_id'])]
    contacts_lst = project_info['contacts']
    for contact in contacts_lst:
        point_of_contacts.append(contact['email'])
        
    # TODO: Send out email to project's creator and points of contacts
    # print(creator, point_of_contacts)
    pass


def send_reject_message(project_info, approver_kerberos, approver_comments):
    """Send a message to the project creator and points of contact indicating
    that the project has been rejected.
    """
    # TODO: Not implemented yet!

    # Get point of contacts
    point_of_contacts = [db.get_project_creator(project_info['project_id'])]
    contacts_lst = project_info['contacts']
    for contact in contacts_lst:
        point_of_contacts.append(contact['email'])
        
    # TODO: Send out email to project's creator and points of contacts
    # print(creator, point_of_contacts)
    pass
