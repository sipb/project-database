#!/usr/bin/python

import datetime

import sqlalchemy as sa
from schema import \
    session, Projects, ContactEmails, Roles, Links, CommChannels, \
    ProjectsHistory, ContactEmailsHistory, RolesHistory, LinksHistory, \
    CommChannelsHistory, CLASS_TO_HISTORY_CLASS_MAP


##############################################################
# Database Operations
##############################################################

# General Purpose Functions

def make_history_entry(x, author_kerberos, action, revision_id):
    """Make a Schema object for the history table representing the added
    object.

    Parameters
    ----------
    x : SQLBase
        The row object.
    author_kerberos : str
        The kerb of the author of the entry.
    action : str
        The action (create, update, delete) being performed.
    revision_id : int
        The revision ID to associate with the action.

    Returns
    -------
    x_history : SQLBase
        The history row object.
    """
    x_history = CLASS_TO_HISTORY_CLASS_MAP[type(x)]()
    for key in x.__table__.columns.keys():
        # Skip 'id' to allow auto-increment:
        if key != 'id':
            setattr(x_history, key, getattr(x, key))

    # Handle edge case of project creation, where project_id is not available
    # in x:
    if (type(x) == Projects) and (x.project_id is None):
        x_history.project_id = get_project_id(x.name)

    x_history.author = author_kerberos
    x_history.action = action
    x_history.revision_id = revision_id
    return x_history


def db_add(x, author_kerberos, action, revision_id):
    """Add an object defined by the Schema to the database, including history
    logging.

    Caller is responsible for committing the change. (This allows transactions
    to succeed/fail together.)

    Parameters
    ----------
    x : SQLBase
        The row object to add.
    author_kerberos : str
        The kerb of the author of the entry.
    action : str
        The action (create, update, delete) being performed.
    revision_id : int
        The revision ID to associate with the action.
    """
    session.add(x)
    x_history = make_history_entry(x, author_kerberos, action, revision_id)
    session.add(x_history)


def db_delete(x, author_kerberos, revision_id):
    """Delete an object specified by the Schema from the database, including
    history logging.

    Caller is responsible for committing the change. (This allows transactions
    to succeed/fail together.)

    Parameters
    ----------
    x : SQLBase
        The row object to delete.
    author_kerberos : str
        The kerb of the author of the entry.
    revision_id : int
        The revision ID to associate with the action.
    """
    x_history = make_history_entry(x, author_kerberos, 'delete', revision_id)
    session.delete(x)
    session.add(x_history)


def db_update_record(current_x, new_x, author_kerberos, revision_id):
    """Update the database to reflect new values for a given row.

    Caller is responsible for committing the change. (This allows transactions
    to succeed/fail together.)

    Parameters
    ----------
    current_x : SQLBase
        The current row.
    new_x : SQLBase
        The new row.
    author_kerberos : str
        The kerb of the author of the entry.
    revision_id : int
        The revision ID to associate with the action.
    """
    changed = False
    for field in current_x.__table__.columns.keys():
        if (
            (field != 'id') and
            (getattr(current_x, field) != getattr(new_x, field))
        ):
            setattr(current_x, field, getattr(new_x, field))
            changed = True

    action = 'update' if changed else 'same'
    x_history = make_history_entry(
        current_x, author_kerberos, action, revision_id
    )
    session.add(x_history)


def make_key_idx_map(x, match_key):
    """Make a dict which maps key strings to indices in the list of records.

    Parameters
    ----------
    x : list of SQLBase
        List of records.
    match_key : str
        The key to match records on.

    Returns
    -------
    key_idx_map : dict
        Dict mapping keys to indices in x.
    """
    return {getattr(x_val, match_key): idx for idx, x_val in enumerate(x)}


def db_update(
    current_x, new_x, match_key, author_kerberos, revision_id
):
    """Update a set of rows to match the new version, tracking
    create/update/delete relationships.

    Caller is responsible for committing the change. (This allows transactions
    to succeed/fail together.)

    Parameters
    ----------
    current_x : list of SQLBase
        The rows as they currently existing in the database.
    new_x : list of SQLBase
        The new entries to put in the database.
    match_key : str
        The column to match on.
    author_kerberos : str
        The kerb of the author of the entry.
    revision_id : int
        The revision ID to associate with the action.
    """
    # Determine what the index of each key is:
    current_key_idx_map = make_key_idx_map(current_x, match_key)
    new_key_idx_map = make_key_idx_map(new_x, match_key)

    # Delete the entries which appear in current_x but not new_x:
    for key, idx in current_key_idx_map.items():
        if key not in new_key_idx_map:
            db_delete(current_x[idx], author_kerberos, revision_id)

    # Add entries which appear in new_x but not current_x, update entries which
    # appear in both:
    for key, idx in new_key_idx_map.items():
        if key in current_key_idx_map:
            db_update_record(
                current_x[current_key_idx_map[key]], new_x[idx],
                author_kerberos, revision_id
            )
        else:
            db_add(new_x[idx], author_kerberos, 'create', revision_id)


def list_dict_convert(query_res_lst, remove_sql_ref=False):
    """Given a list which contains query results from SQLalchemy,
    return a list of their Python dictionary representation
    
    If `remove_sql_ref` set to True, the `_sa_instance_state`
    key automatically inserted by SQLalchemy will be removed 
    from each list entry
    
    Safety: For value safety this function gets the shallow copy
    of each entry's dictionary representation
    
    Source:
    https://stackoverflow.com/questions/1958219/how-to-convert-sqlalchemy-row-object-to-a-python-dict
    """
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
    """Check if a given dictionary has all of the keys defined in req_params (lst)
    """
    res = True
    for param in req_params:
        if param not in dict:
            res = False
    return res


# Get Functions

def get_all_projects():
    """Get metadata all of projects in database
    """
    return session.query(Projects).order_by(
        Projects.status, Projects.name
    ).all()


def get_all_approved_projects():
    """Get data for all approved projects in the database.
    """
    return session.query(Projects).filter_by(
        approval='approved'
    ).order_by(
        Projects.status, Projects.name
    ).all()


def get_all_awaiting_approval_projects():
    """Get data for all projects which are awaiting approval.
    """
    return session.query(Projects).filter_by(
        approval='awaiting_approval'
    ).order_by(
        Projects.status, Projects.name
    ).all()


def get_active_approved_projects():
    """Get data for all active projects in the database.
    """
    return session.query(Projects).filter_by(
        status='active', approval='approved'
    ).order_by(
        Projects.name
    ).all()


def get_inactive_approved_projects():
    """Get data for all inactive projects in the database.
    """
    return session.query(Projects).filter_by(
        status='inactive', approval='approved'
    ).order_by(
        Projects.name
    ).all()


def get_projects_for_contact(email):
    """Get all projects for which the given email is a contact.
    """
    return session.query(Projects).join(
        ContactEmails, Projects.project_id == ContactEmails.project_id
    ).filter(ContactEmails.email == email).order_by(
        Projects.status, Projects.name
    ).all()


def get_project_info(
    model, project_id, raw_input=False, sort_by_index=False, revision_id=None,
    filter_deleted=True
):
    """Given an SQL class model (e.g. ContactEmail, Roles, Links, etc.), query
    that table for all entries associated with project_id and return the result
    in the form of list of dictionaries
    
    If `raw_input` is set to True, we will return the SQLobject instead. This
    allows for direct object modification

    If `sort_by_index` is set to True, the results will be sorted by the index
    column.

    If `revision_id` is provided, it is assumed that `model` is a history
    table, and the results will be filtered by revision ID.

    If `filter_deleted` is provided, it is assumed that `model` is a history
    table, and entries with action == 'delete' will be removed. This has no
    effect if `revision_id` is not provided.
    
    Useful for building higher-level queries
    """
    query = session.query(model).filter_by(project_id=project_id)

    if revision_id is not None:
        query = query.filter_by(revision_id=revision_id)

        # Can only filter delete actions on revisions.
        if filter_deleted:
            query = query.filter(model.action != 'delete')

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
# Tables which have an index column are sorted by the index.

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


def get_project_revision(
    id, revision_id=None, get_raw=False, filter_deleted=True
):
    if revision_id is None:
        return get_project_info(Projects, id, raw_input=get_raw)
    else:
        return get_project_info(
            ProjectsHistory,
            id,
            raw_input=get_raw,
            revision_id=revision_id,
            filter_deleted=filter_deleted
        )


def get_contacts_revision(
    id, revision_id=None, get_raw=False, filter_deleted=True
):
    if revision_id is None:
        return get_project_info(
            ContactEmails, id, raw_input=get_raw, sort_by_index=True
        )
    else:
        return get_project_info(
            ContactEmailsHistory,
            id,
            raw_input=get_raw,
            sort_by_index=True,
            revision_id=revision_id,
            filter_deleted=filter_deleted
        )


def get_roles_revision(
    id, revision_id=None, get_raw=False, filter_deleted=True
):
    if revision_id is None:
        return get_project_info(
            Roles, id, raw_input=get_raw, sort_by_index=True
        )
    else:
        return get_project_info(
            RolesHistory,
            id,
            raw_input=get_raw,
            sort_by_index=True,
            revision_id=revision_id,
            filter_deleted=filter_deleted
        )


def get_links_revision(
    id, revision_id=None, get_raw=False, filter_deleted=True
):
    if revision_id is None:
        return get_project_info(
            Links, id, raw_input=get_raw, sort_by_index=True
        )
    else:
        return get_project_info(
            LinksHistory,
            id,
            raw_input=get_raw,
            sort_by_index=True,
            revision_id=revision_id,
            filter_deleted=filter_deleted
        )


def get_comm_revision(
    id, revision_id=None, get_raw=False, filter_deleted=True
):
    if revision_id is None:
        return get_project_info(
            CommChannels, id, raw_input=get_raw, sort_by_index=True
        )
    else:
        return get_project_info(
            CommChannelsHistory,
            id,
            raw_input=get_raw,
            sort_by_index=True,
            revision_id=revision_id,
            filter_deleted=filter_deleted
        )


def get_project_id(name):
    """Get the ID of a project with `name`, if it exists
    Otherwise returns None
    """
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


def enrich_project_with_auxiliary_fields(project_info, revision_id=None):
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
    project_info['links'] = get_links_revision(
        project_id, revision_id=revision_id
    )
    project_info['comm_channels'] = get_comm_revision(
        project_id, revision_id=revision_id
    )
    project_info['roles'] = get_roles_revision(
        project_id, revision_id=revision_id
    )
    project_info['contacts'] = get_contacts_revision(
        project_id, revision_id=revision_id
    )
    project_info = enrich_project_with_revision_info(
        project_info, revision_id=revision_id
    )
    return project_info


def enrich_project_with_revision_info(project_info, revision_id=None):
    """Add information on the most recent revision to a project_info dict.

    Parameters
    ----------
    project_info : dict
        The project info. This dict will be updated in place.

    Returns
    -------
    project_info : dict
        The updated project info.
    """
    if revision_id is None:
        revision_id = get_current_revision(project_info['project_id'])

    project_id = project_info['project_id']

    history_info = get_project_revision(project_id, revision_id=revision_id)[0]

    project_info['revision_info'] = {
        'timestamp': history_info['timestamp'],
        'editor': history_info['author']
    }
    return project_info


def get_all_info_for_project(project_id, revision_id=None):
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
    project_info = get_project_revision(project_id, revision_id=revision_id)
    if len(project_info) == 0:
        return None
    project_info = project_info[0]
    project_info = enrich_project_with_auxiliary_fields(
        project_info, revision_id=revision_id
    )

    return project_info


def get_all_project_info(filter_method='active', contact_email=None):
    """Get the information for all projects.

    Parameters
    ----------
    filter_method : {'all', 'active', 'inactive'}, optional
        The filter to apply. Options are:
        * 'approved': return all approved projects
        * 'active' (default): return all active approved projects
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
        revision['comm_channels'] = list_dict_convert(
            session.query(CommChannelsHistory).filter_by(
                project_id=project_id, revision_id=revision['revision_id']
            ).all()
        )
    return project_history


def get_now():
    return session.query(sa.func.now()).scalar()


def get_stale_projects(
    now, time_horizon=datetime.timedelta(days=365), active_only=True
):
    """Get projects for which the most recent edit is farther back than the
    specified horizon.

    Parameters
    ----------
    now : datetime.datetime
        The current time. Get this using db.get_now().
    time_horizon : datetime.timedelta, optional
        The time horizon to use. Default is 365 days.
    active_only : bool, optional
        Whether or not to return only active projects (default) or all
        projects (including inactive ones).

    Returns
    -------
    stale_projects : list of dict
        The (full) info for each project. Includes the timestamp of the most
        recent edit in the field 'last_edit_timestamp'.
    """
    most_recent_revision_dates = session.query(
        sa.func.max(ProjectsHistory.timestamp).label('last_edit_timestamp'),
        ProjectsHistory.project_id
    ).group_by(ProjectsHistory.project_id).subquery()

    condition = (
        most_recent_revision_dates.c.last_edit_timestamp <=
        now - time_horizon
    )
    if active_only:
        condition &= (Projects.status == 'active')

    query = session.query(
        Projects, most_recent_revision_dates.c.last_edit_timestamp
    ).join(
        most_recent_revision_dates,
        Projects.project_id == most_recent_revision_dates.c.project_id
    ).filter(condition)
    results = query.all()
    if len(results) > 0:
        stale_projects, last_edit_timestamps = zip(*results)
    else:
        stale_projects = []
        last_edit_timestamps = []

    stale_projects = list_dict_convert(stale_projects)
    stale_projects = [
        enrich_project_with_auxiliary_fields(project_info)
        for project_info in stale_projects
    ]

    for project, last_edit_timestamp in zip(
        stale_projects, last_edit_timestamps
    ):
        project['last_edit_timestamp'] = last_edit_timestamp

    return stale_projects


# Adding operations

def form_row(model, project_id, entry):
    """Form a row object from a dict.

    Parameters
    ----------
    model : type
        A type which inherits from SQLBase.
    project_id : int
        The project ID to use.
    entry : dict
        A dict with keys matching the columns of model.

    Returns
    -------
    result : SQLBase
        The row object.
    """
    result = model()
    result.project_id = int(project_id)
    for key in result.__table__.columns.keys():
        if (key != 'id') and (key != 'project_id') and (key in entry):
            setattr(result, key, entry[key])
    return result


def form_contact_row(project_id, entry):
    """Form a contact row object.

    Parameters
    ----------
    project_id : int
        ID of the project.
    entry : dict
        The contact details. Shall have keys 'type', 'email', and 'index.'

    Returns
    -------
    contact : SQLBase
        The row object.
    """
    return form_row(ContactEmails, project_id, entry)


def form_role_row(project_id, entry):
    """Form a role row object.

    Parameters
    ----------
    project_id : int
        ID of the project.
    entry : dict
        The role details. Shall have keys 'role', 'description', 'index', and
        (optionally) 'prereq'.

    Returns
    -------
    role : SQLBase
        The row object.
    """
    return form_row(Roles, project_id, entry)


def form_link_row(project_id, entry):
    """Form a link row object.

    Parameters
    ----------
    project_id : int
        ID of the project.
    entry : dict
        The link details. Shall have keys 'link', 'index', and (optionally)
        'anchortext'.

    Returns
    -------
    link : SQLBase
        The row object.
    """
    return form_row(Links, project_id, entry)


def form_comms_row(project_id, entry):
    """Form a comms row object.

    Parameters
    ----------
    project_id : int
        ID of the project.
    entry : dict
        The link details. Shall have keys 'commchannel' and 'index'.

    Returns
    -------
    comm : SQLBase
        The row object.
    """
    return form_row(CommChannels, project_id, entry)


def add_project_metadata(args):
    """Add a project with provided metadata to the database. Caller is
    responsible for committing the change.

    Parameters
    ----------
    args : dict
        The project metadata to add. This shall have the keys 'name', 'status',
        'description', and 'creator'. args['status'] shall be one of 'active'
        and 'inactive'.

    Returns
    -------
    project_id : int or None
        The ID of the newly-created project, or None if the operation failed.
    """
    args_lst = ['name', 'status', 'description', 'creator']
    assert check_object_params(args, args_lst)
    assert args['status'] in ['active', 'inactive']
    
    # Check if project already exists
    exists = True if get_project_id(args['name']) else False
    assert not exists

    project = Projects()
    project.name = args['name']
    project.status = args['status']
    project.description = args['description']
    project.creator = args['creator']
    project.approval = args['approval']
    db_add(project, args['creator'], 'create', 0)

    project_id = get_project_id(args['name'])

    return project_id


def add_project_table(
    get_current_fn, form_row_fn, validate_fn, project_id, args,
    author_kerberos, action='create', revision_id=0
):
    """Add entries for a project to a given table. Caller is responsible for
    committing the change.

    Parameters
    ----------
    get_current_fn : callable
        Function which returns the current rows associated with the project.
    form_row_fn : callable
        Function which forms a row object given a dict.
    validate_fn : callable
        Function which validates a list of dicts.
    project_id : int
        The ID of the project to operate on.
    args : list of dict
        The new rows.
    author_kerberos : str
        The kerb of the user adding the rows.
    action : {'create', 'update', 'delete'}, optional
        The action being taken. Default is 'create'.
    revision_id : int, optional 
        The revision ID. Default is 0.

    Returns
    -------
    rows : list of dict
        The rows for the project.
    """
    validate_fn(args)

    for entry in args:
        row = form_row_fn(project_id, entry)
        db_add(row, author_kerberos, action, revision_id)

    return get_current_fn(project_id)


def validate_contacts(args):
    """Validate a list of contacts. Raises AssertionError if invalid.

    Parameters
    ----------
    args : list of dict
        The contacts to validate.
    """
    args_lst = ['type', 'email', 'index']
    for dict in args:
        assert check_object_params(dict, args_lst)
        assert dict['type'] in ['primary', 'secondary']


def add_project_contacts(
    project_id, args, author_kerberos, action='create', revision_id=0
):
    """Add a list of emails associated with a project to the database. Caller
    is responsible for committing the change.

    Parameters
    ----------
    project_id : int
        The ID of the project to add contacts to.
    args : list of dict
        The contacts to add. Each entry shall have keys 'type', 'email', and
        'index'.
    author_kerberos : str
        The kerb of the user adding the contacts.
    action : {'create', 'update', 'delete'}, optional
        The action being taken. Default is 'create'.
    revision_id : int, optional 
        The revision ID. Default is 0.

    Returns
    -------
    contacts : list of dict
        The contacts for the project.
    """
    return add_project_table(
        get_contacts, form_contact_row, validate_contacts, project_id, args,
        author_kerberos, action=action, revision_id=revision_id
    )


def validate_roles(args):
    """Validate a list of roles. Raises AssertionError if invalid.

    Parameters
    ----------
    args : list of dict
        The roles to validate.
    """
    args_lst = ['role', 'description', 'index']  # 'prereq' optional 
    for dict in args:
        assert check_object_params(dict, args_lst)


def add_project_roles(
    project_id, args, author_kerberos, action='create', revision_id=0
):
    """Add a list of roles associated with a project to the database. Caller is
    responsible for committing the change.

    Parameters
    ----------
    project_id : int
        The ID of the project to add contacts to.
    args : list of dict
        The roles to add. Each entry shall have keys 'role', 'description',
        'index', and (optionally) 'prereq'.
    author_kerberos : str
        The kerb of the user adding the roles.
    action : {'create', 'update', 'delete'}, optional
        The action being taken. Default is 'create'.
    revision_id : int, optional 
        The revision ID. Default is 0.

    Returns
    -------
    roles : list of dict
        The roles for the project.
    """
    return add_project_table(
        get_roles, form_role_row, validate_roles, project_id, args,
        author_kerberos, action=action, revision_id=revision_id
    )


def validate_links(args):
    """Validate a list of links. Raises AssertionError if invalid.

    Parameters
    ----------
    args : list of dict
        The links to validate.
    """
    args_lst = ['link', 'index']  # 'anchortext' optional
    for dict in args:
        assert check_object_params(dict, args_lst)


def add_project_links(
    project_id, args, author_kerberos, action='create', revision_id=0
):
    """Add a list of website links associated with a project to the database.
    Caller is responsible for committing the change.

    Parameters
    ----------
    project_id : int
        The ID of the project to add contacts to.
    args : list of dict
        The links to add. Each entry shall have keys 'link', 'index', and
        (optionally) 'anchortext'.
    author_kerberos : str
        The kerb of the user adding the links.
    action : {'create', 'update', 'delete'}, optional
        The action being taken. Default is 'create'.
    revision_id : int, optional 
        The revision ID. Default is 0.

    Returns
    -------
    links : list of dict
        The links for the project.
    """
    return add_project_table(
        get_links, form_link_row, validate_links, project_id, args,
        author_kerberos, action=action, revision_id=revision_id
    )


def validate_comms(args):
    """Validate a list of comm channels. Raises AssertionError if invalid.

    Parameters
    ----------
    args : list of dict
        The comms to validate.
    """
    args_lst = ['commchannel', 'index']
    for dict in args:
        assert check_object_params(dict, args_lst)


def add_project_comms(
    project_id, args, author_kerberos, action='create', revision_id=0
):
    """Add a list of communication channels associated with a project to the
    database CommChannels can be text description rather than just HTML links.
    Caller is responsible for committing the change.
    
    Parameters
    ----------
    project_id : int
        The ID of the project to add contacts to.
    args : list of dict
        The comms to add. Each entry shall have keys 'commchannel' and 'index'.
    author_kerberos : str
        The kerb of the user adding the comms.
    action : {'create', 'update', 'delete'}, optional
        The action being taken. Default is 'create'.
    revision_id : int, optional 
        The revision ID. Default is 0.

    Returns
    -------
    comms : list of dict
        The comms for the project.
    """
    return add_project_table(
        get_comm, form_comms_row, validate_comms, project_id, args,
        author_kerberos, action=action, revision_id=revision_id
    )


def add_project(
    project_info, creator_kerberos, initial_approval='awaiting_approval'
):
    """Add the given project to the database and commits the change.

    Raises ValueError if project with the given name already exists.

    Parameters
    ----------
    project_info : dict
        The project info extracted from the form in performaddproject.html
    creator_kerberos : str
        The kerberos of the user who created the project.
    initial_approval : {'awaiting_approval', 'approved', 'rejected'}, optional
        The initial approval status of the project. Default is
        'awaiting_approval'.

    Returns
    -------
    project_id : int
        If success, return the project_id (primary key) for the newly-added
        project.
    """
    project_id = get_project_id(project_info['name'])
    if project_id:
        raise ValueError('Project with that name already exists!')
    
    metadata = {
        'name': project_info['name'],
        'description': project_info['description'],
        'status': project_info['status'],
        'creator': creator_kerberos,
        'approval': initial_approval
    }
    project_id = add_project_metadata(metadata)
    add_project_links(project_id, project_info['links'], creator_kerberos)
    add_project_comms(
        project_id, project_info['comm_channels'], creator_kerberos
    )
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
    editor_kerberos : str
        The kerb of the user making the edit.
    """
    allowed_fields = [
        'name', 'description', 'status', 'approval', 'approver',
        'approver_comments'
    ]
    metadata = get_project(project_id, True)[0]  # Returns SQL object
    
    for field in allowed_fields:  # Only look for changes in the allowed fields
        if (field in args) and (args[field] != getattr(metadata, field)):
            setattr(metadata, field, args[field])

    revision_id = get_current_revision(project_id) + 1

    # Log the changes
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
    project_history.revision_id = revision_id
    session.add(project_history)

    return revision_id


def update_project_table(
    get_current_fn, form_row_fn, match_key, project_id, args, editor_kerberos,
    revision_id
):
    """Update a given table with new entries. Caller is responsible for
    committing the change.

    Parameters
    ----------
    get_current_fn : callable
        Function which returns the current rows associated with the project.
    form_row_fn : callable
        Function which forms a row object given a dict.
    match_key : str
        Key to match entries on.
    project_id : int
        The ID of the project to operate on.
    args : list of dict
        The new rows.
    editor_kerberos : str
        The kerb of the user making the edit.
    revision_id : int
        The revision ID associated with the edit.
    """
    current_x = get_current_fn(project_id, get_raw=True)

    new_x = []
    for entry in args:
        new_x.append(form_row_fn(project_id, entry))

    db_update(
        current_x, new_x, match_key, editor_kerberos, revision_id
    )


def update_project_contacts(project_id, args, editor_kerberos, revision_id):
    """Update the contact email entries for a project in the database.
    Caller is responsible for committing the change.

    Parameters
    ----------
    project_id : int
        ID of the project we want to modify
    args : list of dict
        - args is a list of dictionaries with keys 'type', 'email', and 'index'
        - 'type' is either 'primary' or 'secondary'
    editor_kerberos : str
        The kerb of the user making the edit.
    revision_id : int
        The revision ID associated with the edit.
    """
    update_project_table(
        get_contacts, form_contact_row, 'email', project_id, args,
        editor_kerberos, revision_id
    )


def update_project_roles(project_id, args, editor_kerberos, revision_id):
    """Update the roles entries for a project in the database.
    Caller is responsible for committing the change.

    Parameters
    ----------
    project_id : int
        ID of the project we want to modify
    args : dict
        - args is a list of dictionaries with keys 'role', 'description', and
            (optional) 'prereq' 
        - 'type' is either 'primary' or 'secondary'
    editor_kerberos : str
        The kerb of the user making the edit.
    revision_id : int
        The revision ID associated with the edit.
    """
    update_project_table(
        get_roles, form_role_row, 'role', project_id, args, editor_kerberos,
        revision_id
    )


def update_project_links(project_id, args, editor_kerberos, revision_id):
    """Update the links entries for a project in the database.
    Caller is responsible for committing the change.

    Parameters
    ----------
    project_id : int
        ID of the project we want to modify
    args : dict
        - args is a list of dictionaries with keys 'link' and (optional)
            'anchortext'.
    editor_kerberos : str
        The kerb of the user making the edit.
    revision_id : int
        The revision ID associated with the edit.
    """
    update_project_table(
        get_links, form_link_row, 'link', project_id, args, editor_kerberos,
        revision_id
    )


def update_project_comms(project_id, args, editor_kerberos, revision_id):
    """Update the communication channels entries for a project in the database.
    Caller is responsible for committing the change.

    Parameters
    ----------
    project_id : int
        ID of the project we want to modify
    args : dict
        - args is a list of dictionaries with keys 'commchannel'
    editor_kerberos : str
        The kerb of the user making the edit.
    revision_id : int
        The revision ID associated with the edit.
    """
    update_project_table(
        get_comm, form_comms_row, 'commchannel', project_id, args,
        editor_kerberos, revision_id
    )


def update_project_auxiliary_tables(
    project_info, project_id, editor_kerberos, revision_id
):
    update_project_links(
        project_id, project_info['links'], editor_kerberos, revision_id
    )
    update_project_comms(
        project_id, project_info['comm_channels'], editor_kerberos, revision_id
    )
    update_project_contacts(
        project_id, project_info['contacts'], editor_kerberos, revision_id
    )
    update_project_roles(
        project_id, project_info['roles'], editor_kerberos, revision_id
    )


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
        Return a dictionary formatted like `project_info` representing the view
        of the project prior to making the update.
    """
    project_exists = True if get_project_name(project_id) else False
    if not project_exists:
        raise ValueError('No project with id %d exists!' % int(project_id))

    new_metadata = {
        'name': project_info['name'], 
        'description': project_info['description'],
        'status': project_info['status']
        # `creator` and `approval` fields are intentionally not supplied
    }
    orig_project = get_all_info_for_project(project_id)
    revision_id = update_project_metadata(
        project_id, new_metadata, editor_kerberos
    )
    update_project_auxiliary_tables(
        project_info, project_id, editor_kerberos, revision_id
    )
    session.commit()
    return orig_project


def approve_project(
    project_info, project_id, approver_kerberos, approver_comments
):
    """Approve a project.

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
    # Change status to "approved"
    new_metadata = {
        'approval': 'approved',
        'approver': approver_kerberos,
        'approver_comments': approver_comments
    }
    revision_id = update_project_metadata(
        project_id, new_metadata, approver_kerberos
    )
    update_project_auxiliary_tables(
        project_info, project_id, approver_kerberos, revision_id
    )
    session.commit()


def reject_project(
    project_info, project_id, approver_kerberos, approver_comments
):
    """Reject a project.

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
    # Change status to "rejected"
    new_metadata = {
        'approval': 'rejected',
        'approver': approver_kerberos,
        'approver_comments': approver_comments
    }
    revision_id = update_project_metadata(
        project_id, new_metadata, approver_kerberos
    )
    update_project_auxiliary_tables(
        project_info, project_id, approver_kerberos, revision_id
    )
    session.commit()


def set_project_status_to_awaiting_approval(
    project_info, project_id, editor_kerberos
):
    """Set a project back to "awaiting_approval"

    Parameters
    ----------
    project_info : dict
        The project info extracted from the form.
    project_id : int or str
        The project ID for the existing project.
    editor_kerberos : str
        The kerberos of the user editing the project.
    """
    # Change status to "rejected"
    new_metadata = {
        'approval': 'awaiting_approval'
    }
    revision_id = update_project_metadata(
        project_id, new_metadata, editor_kerberos
    )
    update_project_auxiliary_tables(
        project_info, project_id, editor_kerberos, revision_id
    )
    session.commit()


def rollback_project(project_id, revision_id, editor_kerberos):
    """Roll back a project's state to the given revision ID.

    Parameters
    ----------
    project_id : int
        The project ID to modify.
    revision_id : int
        The revision ID to roll back to.
    editor_kerberos : str
        The username of the person performing the rollback.
    """
    project_exists = True if get_project_name(project_id) else False
    if not project_exists:
        raise ValueError('No project with id %d exists!' % int(project_id))

    project_info = get_all_info_for_project(
        project_id, revision_id=revision_id
    )
    if project_info is None:
        raise ValueError('No revision with id %d exists!' % int(revision_id))

    rollback_revision_id = update_project_metadata(
        project_id, project_info, editor_kerberos
    )
    update_project_auxiliary_tables(
        project_info, project_id, editor_kerberos, rollback_revision_id
    )
    session.commit()

    
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
