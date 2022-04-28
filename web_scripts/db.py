#!/usr/bin/python

import sqlalchemy as sa
from schema import \
    session, Projects, ContactEmails, Roles, Links, CommChannels, \
    ProjectsHistory, ContactEmailsHistory, RolesHistory, LinksHistory


##############################################################
# Database Operations
##############################################################

# General Purpose Functions

def db_add(x):
    '''Add an object defined by the Schema to the database

    Caller is responsible for committing the change. (This allows transactions
    to succeed/fail together.)
    '''
    session.add(x)


def list_dict_convert(query_res_lst, remove_sql_ref=False):
    '''
    Given a list which contains query results from SQLalchemy,
    return a list of their Python dictionary representation
    
    If `remove_sql_ref` set to True, the `_sa_instance_state`
    key automatically inserted by SQLalchemy will be removed 
    from each list entry
    
    Safety: For value safety this function gets the shallow copy
    of each entry's dictionary representation
    
    Source: https://stackoverflow.com/questions/1958219/how-to-convert-sqlalchemy-row-object-to-a-python-dict
    '''
    if remove_sql_ref:
        converted_lst = []
        for entry in query_res_lst:
            entry_dict = entry.__dict__.copy()
            entry_dict.pop('_sa_instance_state')
            converted_lst.append(entry_dict)
        return converted_lst
    else:
        return [r.__dict__.copy() for r in query_res_lst]


def check_object_params(dict, req_params):
    '''
    Check if a given dictionary has all of the keys defined in req_params (lst)
    '''
    res = True
    for param in req_params:
        if param not in dict:
            res = False
    return res


# Get Functions

def get_all_projects():
    '''Get metadata all of projects in database'''
    return session.query(Projects).all()


def get_all_approved_projects():
    """Get data for all approved projects in the database.
    """
    return session.query(Projects).filter_by(approval='approved').all()


def get_all_awaiting_approval_projects():
    """Get data for all projects which are awaiting approval.
    """
    return session.query(Projects).filter_by(
        approval='awaiting_approval'
    ).all()


def get_active_approved_projects():
    """Get data for all active projects in the database.
    """
    return session.query(Projects).filter_by(
        status='active', approval='approved'
    ).all()


def get_inactive_approved_projects():
    """Get data for all inactive projects in the database.
    """
    return session.query(Projects).filter_by(
        status='inactive', approval='approved'
    ).all()


def get_projects_for_contact(email):
    """Get all projects for which the given email is a contact.
    """
    return session.query(Projects).join(
        ContactEmails, Projects.project_id == ContactEmails.project_id
    ).filter(ContactEmails.email == email).all()


def get_project_info(model, project_id, raw_input=False, sort_by_index=False):
    '''
    Given an SQL class model (e.g. ContactEmail, Roles, Links, etc.), query
    that table for all entries associated with project_id and return the result
    in the form of list of dictionaries
    
    If `raw_input` is set to True, we will return the SQLobject instead. This
    allows for direct object modification

    If `sort_by_index` is set to True, the results will be sorted by the index
    column.
    
    Useful for building higher-level queries
    '''
    query = session.query(model).filter_by(project_id=project_id)
    if sort_by_index:
        query = query.order_by(model.index)
    sql_result = query.all()
    if raw_input:
        return sql_result
    else:
        return list_dict_convert(sql_result, True)


# Shorthand functions to get all table entries associated with a project ID
# `id` 
# If `get_raw` is set to True, return SQL object instead of dictionary.

get_project = lambda id, get_raw=False: get_project_info(
    Projects, id, get_raw
)  # Return maximum 1 result
get_contacts = lambda id, get_raw=False: get_project_info(
    ContactEmails, id, get_raw, sort_by_index=True
)
get_roles = lambda id, get_raw=False: get_project_info(
    Roles, id, get_raw, sort_by_index=True
)
get_links = lambda id, get_raw=False: get_project_info(
    Links, id, get_raw, sort_by_index=True
)
get_comm = lambda id, get_raw=False: get_project_info(
    CommChannels, id, get_raw, sort_by_index=True
)


def get_project_id(name):
    '''
    Get the ID of a project with `name`, if it exists
    Otherwise returns None
    '''
    return session.query(Projects.project_id).filter_by(name=name).scalar()


def get_project_name(project_id):
    """Get the name of the project with the given project_id, if it exists.
    Otherwise returns None.
    """
    return session.query(
        Projects.name
    ).filter_by(project_id=project_id).scalar()


def get_project_creator(project_id):
    """Get the kerberos of the creator of the project with the given
    project_id, if it exists. Otherwise returns None.
    """
    return session.query(
        Projects.creator
    ).filter_by(project_id=project_id).scalar()


def get_project_approval_status(project_id):
    """Get the approval status of the project with the given project_id, if it
    exists. Otherwise returns None.
    """
    return session.query(
        Projects.approval
    ).filter_by(project_id=project_id).scalar()


def enrich_project_with_auxiliary_fields(project_info):
    """Add the links, comm_channels, roles, and contacts info to a project_info
    dict.

    Parameters
    ----------
    project_info : dict
        The project info. This dict will be updated in place.

    Returns
    -------
    project_info : dict
        The updated project info.
    """
    project_id = project_info['project_id']
    project_info['links'] = get_links(project_id)
    project_info['comm_channels'] = get_comm(project_id)
    project_info['roles'] = get_roles(project_id)
    project_info['contacts'] = get_contacts(project_id)
    return project_info


def get_all_info_for_project(project_id):
    """Get all of the information for a specific project.

    Parameters
    ----------
    project_id : str or int
        The project ID to get information for.

    Returns
    -------
    project_info : dict
        The information on the specified project.
    """
    project_info = get_project(project_id)[0]
    project_info = enrich_project_with_auxiliary_fields(project_info)

    return project_info


def get_all_project_info(filter_method='approved', contact_email=None):
    """Get the information for all projects.

    Parameters
    ----------
    filter_method : {'all', 'active', 'inactive'}, optional
        The filter to apply. Options are:
        * 'approved' (default): return all approved projects
        * 'active': return all active approved projects
        * 'inactive': return all inactive approved projects
        * 'contact': return projects for which the given contact_email is in
            the contact list.
        * 'awaiting_approval': return projects which are awaiting approval.
    contact_email : str, optional
        The contact email to filter on when filter_method is 'contact'.

    Returns
    -------
    project_list : list of dict
        List of all projects.
    """
    if filter_method == 'approved':
        projects = get_all_approved_projects()
    elif filter_method == 'active':
        projects = get_active_approved_projects()
    elif filter_method == 'inactive':
        projects = get_inactive_approved_projects()
    elif filter_method == 'contact':
        projects = get_projects_for_contact(contact_email)
    elif filter_method == 'awaiting_approval':
        projects = get_all_awaiting_approval_projects()
    else:
        raise ValueError('Unknown status filter!')

    project_list = list_dict_convert(projects)
    # There's probably a way to do this with joins...
    project_list = [
        enrich_project_with_auxiliary_fields(project_info)
        for project_info in project_list
    ]
        
    return project_list


def get_current_revision(project_id):
    """Get the current revision ID for the given project.

    Parameters
    ----------
    project_id : int
        The project ID to get the current revision ID for.

    Returns
    -------
    revision_id : int
        The current revision's ID.
    """
    return session.query(
        sa.func.max(ProjectsHistory.revision_id)
    ).filter_by(project_id=project_id).one()[0]


def get_project_history(project_id):
    """Get all revisions for the given project.

    Parameters
    ----------
    project_id : int
        The project ID to fetch.

    Returns
    -------
    project_history : list of dict
        The project history.
    """
    project_history = list_dict_convert(
        session.query(ProjectsHistory).filter_by(project_id=project_id).all()
    )
    for revision in project_history:
        revision['contacts'] = list_dict_convert(
            session.query(ContactEmailsHistory).filter_by(
                project_id=project_id, revision_id=revision['revision_id']
            ).all()
        )
        revision['roles'] = list_dict_convert(
            session.query(RolesHistory).filter_by(
                project_id=project_id, revision_id=revision['revision_id']
            ).all()
        )
        revision['links'] = list_dict_convert(
            session.query(LinksHistory).filter_by(
                project_id=project_id, revision_id=revision['revision_id']
            ).all()
        )
    return project_history


# Adding operations

def add_project_metadata(args):
    '''
    Add a project with provided metadata to the database. Caller is responsible
    for committing the change.
    
    Requires: 
        - args to have keys of 'name', 'status', 'description', 'creator' with
            valid types
        - status is either 'active' or 'inactive'
        
    Returns: 
        - project_id associated with newly created project, None if project
            already exists or invalid arguments
    '''
    try:
        args_lst = ['name', 'status', 'description', 'creator']
        assert check_object_params(args, args_lst)
        assert args['status'] in ['active', 'inactive']
    except AssertionError:
        return None
    
    # Check if project already exists
    exists = True if get_project_id(args['name']) else False
    if exists:
        return None

    project = Projects()
    project.name = args['name']
    project.status = args['status']
    project.description = args['description']
    project.creator = args['creator']
    # Projects are waiting to be approved by default
    project.approval = 'awaiting_approval'
    db_add(project)

    project_id = get_project_id(args['name'])

    project_history = ProjectsHistory()
    project_history.project_id = project_id
    project_history.name = project.name
    project_history.description = project.description
    project_history.status = project.status
    project_history.approval = project.approval
    project_history.creator = project.creator
    project_history.author = args['creator']
    project_history.action = 'create'
    project_history.revision_id = 0
    db_add(project_history)

    return project_id


def add_project_contacts(
    project_id, args, author_kerberos, action='create', revision_id=0
):
    '''
    Add a list of emails associated with a project to the database. Caller is
    responsible for committing the change.
    
    Requires: 
        - project_id to be a valid project ID in the Contacts table
        - args to be list of dictionaries with keys 'type','email' 
        - key 'type' is either 'primary' or 'secondary'
        
    Returns: 
        - None if no project with that name or invalid arguments, otherwise 
        returns list of all emails associated with project in DB
    '''
    try:
        args_lst = ['type', 'email', 'index']
        for dict in args:
            assert check_object_params(dict, args_lst)
            assert dict['type'] in ['primary', 'secondary']
    except AssertionError:
        return None
    
    for entry in args:
        contact = ContactEmails()
        contact.project_id = project_id
        contact.type = entry['type']
        contact.email = entry['email']
        contact.index = entry['index']
        db_add(contact)

        contact_history = ContactEmailsHistory()
        contact_history.project_id = project_id
        contact_history.type = contact.type
        contact_history.email = contact.email
        contact_history.index = contact.index
        contact_history.author = author_kerberos
        contact_history.action = action
        contact_history.revision_id = revision_id
        db_add(contact_history)

    return get_contacts(project_id)


def add_project_roles(
    project_id, args, author_kerberos, action='create', revision_id=0
):
    '''
    Add a list of roles associated with a project to the database. Caller is
    responsible for committing the change.
    
    Requires: 
        - project_id to be a valid project ID in the Roles table
        - args to be list of dictionaries with keys 'role', 'description',
            'index', and (optional) 'prereq' 
        
    Returns: 
        - None if no project with that name or invalid arguments, otherwise
            returns list of all roles associated with project in DB
    '''
    try:
        args_lst = ['role', 'description', 'index']  # 'prereq' optional 
        for dict in args:
            assert check_object_params(dict, args_lst)
    except AssertionError:
        return None
    
    for entry in args:
        role = Roles()
        role.project_id = project_id
        role.role = entry['role']
        role.description = entry['description']
        role.index = entry['index']
        if 'prereq' in entry:
            role.prereq = entry['prereq']
        db_add(role)

        role_history = RolesHistory()
        role_history.project_id = role.project_id
        role_history.role = role.role
        role_history.description = role.description
        role_history.index = role.index
        role_history.prereq = role.prereq
        role_history.author = author_kerberos
        role_history.action = action
        role_history.revision_id = revision_id
        db_add(role_history)

    return get_roles(project_id)


def add_project_links(
    project_id, args, author_kerberos, action='create', revision_id=0
):
    '''
    Add a list of website links associated with a project to the database.
    Caller is responsible for committing the change.
    
    Requires: 
        - project_id to be a valid project ID in the Links table
        - args to be list of dicts with keys 'link' and 'index'
        
    Returns: 
        - None if no project with that name or invalid arguments, otherwise 
            returns list of all links associated with project in DB
    '''
    try:
        args_lst = ['link', 'index']  # 'prereq' optional 
        for dict in args:
            assert check_object_params(dict, args_lst)
    except AssertionError:
        return None

    for entry in args:
        link = Links()
        link.project_id = project_id
        link.link = entry['link']
        link.index = entry['index']
        db_add(link)

        link_history = LinksHistory()
        link_history.project_id = link.project_id
        link_history.link = link.link
        link_history.index = link.index
        link_history.author = author_kerberos
        link_history.action = action
        link_history.revision_id = revision_id
        db_add(link_history)

    return get_links(project_id)


def add_project_comms(project_id, args):
    '''
    Add a list of communication channels associated with a project to the
    database CommChannels can be text description rather than just HTML links.
    Caller is responsible for committing the change.
    
    Requires: 
        - project_id to be a valid project ID in the Comms table
        - args to be list of dicts with keys 'commchannel' and 'index'
        
    Returns: 
        - None if no project with that name or invalid arguments, otherwise 
            returns list of all communication channels associated with project
            in DB
    '''
    try:
        args_lst = ['commchannel', 'index']  # 'prereq' optional 
        for dict in args:
            assert check_object_params(dict, args_lst)
    except AssertionError:
        return None

    for entry in args:
        comm = CommChannels()
        comm.project_id = project_id
        comm.commchannel = entry['commchannel']
        comm.index = entry['index']
        db_add(comm)
    return get_comm(project_id)


def add_project(project_info, creator_kerberos):
    """Add the given project to the database and commits the change.

    Parameters
    ----------
    project_info : dict
        The project info extracted from the form in performaddproject.html
    creator_kerberos : str
        The kerberos of the user who created the project.

    Returns
    -------
    project_id : int
        If success, return the project_id (primary key) for the newly-added
        project. Otherwise, return -1
    """
    project_id = get_project_id(project_info['name'])
    if project_id:
        return -1  # Project already exists
    
    metadata = {
        'name': project_info['name'],
        'description': project_info['description'],
        'status': project_info['status'],
        'creator': creator_kerberos,
    }
    project_id = add_project_metadata(metadata)
    add_project_links(project_id, project_info['links'], creator_kerberos)
    add_project_comms(project_id, project_info['comm_channels'])
    add_project_contacts(
        project_id, project_info['contacts'], creator_kerberos
    )
    add_project_roles(project_id, project_info['roles'], creator_kerberos)
    session.commit()
    return project_id


# Update an existing project

def update_project_metadata(project_id, args, editor_kerberos):
    """Update the metadata entries for a project in the database.
    Only the name, description, and status can be changed.
    Caller is responsible for committing the change.

    Parameters
    ----------
    project_id : int
        ID of the project we want to modify
    args : dict
        Keys are fields in the Projects table, and values fit the
        right type and correct value according to schema.
    """
    allowed_fields = [
        'name', 'description', 'status', 'approval', 'approver',
        'approver_comments'
    ]
    metadata = get_project(project_id, True)[0]  # Returns SQL object
    
    for field in allowed_fields:  # Only look for changes in the allowed fields
        if (field in args) and (args[field] != getattr(metadata, field)):
            setattr(metadata, field, args[field])

    project_history = ProjectsHistory()
    project_history.project_id = project_id
    project_history.name = metadata.name
    project_history.description = metadata.description
    project_history.status = metadata.status
    project_history.approval = metadata.approval
    project_history.creator = metadata.creator
    project_history.approver = metadata.approver
    project_history.approver_comments = metadata.approver_comments
    project_history.author = editor_kerberos
    project_history.action = 'update'
    project_history.revision_id = get_current_revision(project_id) + 1
    db_add(project_history)

###############################################################################
# Update Logic:
###############################################################################
# For tables outside of the original metadata, we handle updating by deleting
# all current email entries and then adding back provided ones in `args`.
#
# In the future, we may consider inserting the deleted entries into an archival
# table for logging / history purposes.
###############################################################################


def update_project_contacts(project_id, args, editor_kerberos):
    """Update the contact email entries for a project in the database.
    Caller is responsible for committing the change.

    Parameters
    ----------
    project_id : int
        ID of the project we want to modify
    args : list of dict
        - args is a list of dictionaries with keys 'type', 'email', and 'index'
        - key 'type' is either 'primary' or 'secondary'
    """
    revision_id = get_current_revision(project_id)

    # Delete current contact entries, logging the deletions:
    query_command = session.query(ContactEmails).filter_by(
        project_id=project_id
    )

    for contact in query_command.all():
        contact_history = ContactEmailsHistory()
        contact_history.project_id = project_id
        contact_history.type = contact.type
        contact_history.email = contact.email
        contact_history.index = contact.index
        contact_history.author = editor_kerberos
        contact_history.action = 'delete'
        contact_history.revision_id = revision_id
        db_add(contact_history)

    query_command.delete()
    
    # Add the new contact list    
    add_project_contacts(
        project_id, args, editor_kerberos, action='create',
        revision_id=revision_id
    )


def update_project_roles(project_id, args, editor_kerberos):
    """Update the roles entries for a project in the database.
    Caller is responsible for committing the change.

    Parameters
    ----------
    project_id : int
        ID of the project we want to modify
    args : dict
        - args is a list of dictionaries with keys 'role', 'description', and
            (optional) 'prereq' 
        - key 'type' is either 'primary' or 'secondary'
    """
    revision_id = get_current_revision(project_id)

    # Delete current roles entries
    query_command = session.query(Roles).filter_by(project_id=project_id)

    for role in query_command.all():
        role_history = RolesHistory()
        role_history.project_id = role.project_id
        role_history.role = role.role
        role_history.description = role.description
        role_history.prereq = role.prereq
        role_history.index = role.index
        role_history.author = editor_kerberos
        role_history.action = 'delete'
        role_history.revision_id = revision_id
        db_add(role_history)

    query_command.delete()
    
    # Add the new roles list    
    add_project_roles(
        project_id, args, editor_kerberos, action='create',
        revision_id=revision_id
    )


def update_project_links(project_id, args, editor_kerberos):
    """Update the links entries for a project in the database.
    Caller is responsible for committing the change.

    Parameters
    ----------
    project_id : int
        ID of the project we want to modify
    args : dict
        - args is a list of dictionaries with keys 'link'
    """
    revision_id = get_current_revision(project_id)

    # Delete current link entries
    query_command = session.query(Links).filter_by(project_id=project_id)

    for link in query_command.all():
        link_history = LinksHistory()
        link_history.project_id = project_id
        link_history.link = link.link
        link_history.index = link.index
        link_history.author = editor_kerberos
        link_history.action = 'delete'
        link_history.revision_id = revision_id
        db_add(link_history)

    query_command.delete()

    # Add the new link list    
    add_project_links(
        project_id, args, editor_kerberos, action='create',
        revision_id=revision_id
    )


def update_project_comms(project_id, args):
    """Update the communication channels entries for a project in the database.
    Caller is responsible for committing the change.

    Parameters
    ----------
    project_id : int
        ID of the project we want to modify
    args : dict
        - args is a list of dictionaries with keys 'commchannel'
    """
    # Delete current comm entries
    query_command = session.query(CommChannels).filter_by(
        project_id=project_id
    )
    query_command.delete()

    # Add the new comms list    
    add_project_comms(project_id, args)


def update_project(project_info, project_id, editor_kerberos):
    """Update the information for the given project in the database and commits
    the change.

    Parameters
    ----------
    project_info : dict
        The project info extracted from the form.
    project_id : int or str
        The project ID for the existing project.
    editor_kerberos : str
        The kerberos of the user editing the project.
        
    Returns
    -------
    original_project : dict, int
        Return -1 if there is no project with ID `project_id`.
        Otherwise return a dictionary formatted like `project_info` 
        representing the view of the project prior to making the update,
    """
    project_exists = True if get_project_name(project_id) else False
    if not project_exists:
        return -1  # There's no existing project with that ID
    new_metadata = {
        'name': project_info['name'], 
        'description': project_info['description'],
        'status': project_info['status']
        # `creator` and `approval` fields are intentionally not supplied
    }
    orig_project = get_all_info_for_project(project_id)
    update_project_metadata(project_id, new_metadata, editor_kerberos)
    update_project_links(project_id, project_info['links'], editor_kerberos)
    update_project_comms(project_id, project_info['comm_channels'])
    update_project_contacts(
        project_id, project_info['contacts'], editor_kerberos
    )
    update_project_roles(project_id, project_info['roles'], editor_kerberos)
    session.commit()
    return orig_project


def approve_project(
    project_info, project_id, approver_kerberos, approver_comments
):
    """Approve a project. This should update the database and send an email to
    the project's creator and points-of-contact.

    Parameters
    ----------
    project_info : dict
        The project info extracted from the form.
    project_id : int or str
        The project ID for the existing project.
    approver_kerberos : str
        The kerberos of the user approving the project.
    approver_comments : str
        The approver's comments on the project.
    """
    creator = None
    point_of_contacts = []
    
    # Change status to "approved"
    new_metadata = {
        'approval': 'approved',
        'approver': approver_kerberos,
        'approver_comments': approver_comments
    }
    update_project_metadata(project_id, new_metadata, approver_kerberos)
    session.commit()
    
    # Get point of contacts
    metadata = get_project(project_id, True)[0]  # Returns SQL object
    creator = metadata.creator  # Get creator
    contacts_lst = get_contacts(project_id)
    for contact in contacts_lst:
        point_of_contacts.append(contact['email'])
    
    # TODO: Send out email to project's creator and points of contacts
    # print(creator, point_of_contacts)
    pass


def reject_project(
    project_info, project_id, approver_kerberos, approver_comments
):
    """Reject a project. This should update the database and send an email to
    the project's creator and points-of-contact.

    Parameters
    ----------
    project_info : dict
        The project info extracted from the form.
    project_id : int or str
        The project ID for the existing project.
    approver_kerberos : str
        The kerberos of the user approving the project.
    approver_comments : str
        The approver's comments on the project.
    """
    creator = None
    point_of_contacts = []
    
    # Change status to "rejected"
    new_metadata = {
        'approval': 'rejected',
        'approver': approver_kerberos,
        'approver_comments': approver_comments
    }
    update_project_metadata(project_id, new_metadata, approver_kerberos)
    session.commit()

    # Get point of contacts
    metadata = get_project(project_id, True)[0]  # Returns SQL object
    creator = metadata.creator  # Set creator
    contacts_lst = get_contacts(project_id)
    for contact in contacts_lst:
        point_of_contacts.append(contact['email'])
        
    # TODO: Send out email to project's creator and points of contacts
    # print(creator, point_of_contacts)
    pass

    
######################################################################
# Testing Code 
######################################################################

# Example usage
# project = {
#         "name":"SIPB Minecraft",
#         "status":"active",
#         "description":"Virtual MIT in a Minecraft server!"
#         }
# add_project(project)

# print(get_all_projects())
# pj1 = {
#     'name':'test1',
#     'status':'active',
#     'description':'that is all folks'
# }
# print(add_project_metadata(pj1))
# print(get_project_id('test1'))
# print(get_all_projects())

# contacts1 =[
#     {
#         'type':'primary',
#         'email':'you-fools@mit.edu',
#     },
#     {
#         'type':'secondary',
#         'email':'ec-discuss-never@mit.edu'
#     }
# ]
# project_id = get_project_id('test')
# update_project_contacts(project_id,contacts1)

# project_id = get_project_id('test1')
# print(get_contacts(project_id))

# roles1 = [
#     {
#         'role':'Support Tech',
#         'description':'get familiar with MIT\'s and SIPB\'s computing infrastructure by helping answer user questions and approve user requests.'
#         # missing prereq
#     },
#     {
#         'role':'Support Tech',
#         'description':"help design, implement, test, and review SIPB's cluster management software.",
#         'prereq':'previous programming experience in any statically typed language, knowledge of Python and Go or ability to independently learn them, 6.033-level understanding of computer systems, experience with Git, experience with Linux'
#     }
# ]
# #print(add_project_roles('test1',roles1))

# links1 = [
#     {'link':'https://sipb.mit.edu/'},
#     {'link':'https://hwops.mit.edu/'}
# ]
# print(update_project_links(1,links1))

# comms1 = [
#     {'commchannel':'sipb-hwops@mit.edu'},
# ]
# #print(add_project_comms('test1',comms1))


# print("Done")

# project_mod = {
#         "name":"SIPB Takes Over the World",
#         "status":"active",
#         "description":"April Fools"
# }
    
# print(update_metadata(1, project_mod))
    
# update_project1 = {
# 'name': 'myproject',
# 'description': 'something something something',
# 'status': 'active',
# 'links': [{'link':'http://link.com'}],
# 'comm_channels': [{'commchannel':'sipb-hwops@mit.edu'}],
# 'contacts': [{'email': 'markchil@mit.edu', 'type': 'primary'}],
# 'roles': [{'role': 'support tech', 'description': 'do stuff', 'prereq': None}]
# }

# print(update_project(update_project1,3,'huydai'))

# reject_project(dict(),1,'huydai','it is bad')
# approve_project(dict(),3,'huydai','it is good')
