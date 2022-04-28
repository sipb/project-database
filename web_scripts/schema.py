#!/usr/bin/python

import sqlalchemy as db
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import creds

DATABASE_NAME = creds.database_name
SQL_URL = "mysql://%s:%s@sql.mit.edu/%s" % (
    creds.user, creds.password, DATABASE_NAME
)


##############################################################
# Setup Stages
##############################################################

# Initialization Steps
SQLBase = db.ext.declarative.declarative_base()
sqlengine = db.create_engine(SQL_URL)
SQLBase.metadata.bind = sqlengine
session = db.orm.sessionmaker(bind=sqlengine)()  # main object used for queries

# Implement schema
SQLBase.metadata.create_all(sqlengine)

# Strategy: Every table has a version which stores the current state, and a
# separate "history table" which contains the edit history. This is done to
# ensure that it is easy to make queries against the current state without
# having to understand the history tracking mechanism. To implement this, every
# table has a "Base" which inherits from object and defines all columns. The
# main table then inherits from the "Base" class and SQLBase. The history table
# then inherits from the "Base" class, SQLBase, and the HistoryMixin which adds
# the columns needed for edit logging. (Columns which have different
# constraints in the main table vs. the history table are defined in the
# subclasses.) 


class HistoryMixin(object):
    author = db.Column(db.String(50), nullable=False)
    # action can be 'create', 'update', 'delete'
    action = db.Column(db.String(25), nullable=False)
    revision_id = db.Column(db.Integer(), nullable=False)
    timestamp = db.Column(
        db.TIMESTAMP, nullable=False, server_default=db.func.now()
    )


class ProjectsBase(object):
    # project_id and name must be defined in subclasses, as they have special
    # constraints.

    description = db.Column(db.Text(), nullable=False)
    # status can be "active" or "inactive"
    status = db.Column(db.String(25), nullable=False)
    # approval can be "awaiting_approval" or "approved" or "rejected"
    approval = db.Column(db.String(25), nullable=False)
    # Kerb of user who registered the project:
    creator = db.Column(db.String(50), nullable=False)
    # Kerb of user who approved the project:
    approver = db.Column(db.String(50), nullable=True)
    # Comments from user who approved the project:
    approver_comments = db.Column(db.Text(), nullable=True)


class Projects(SQLBase, ProjectsBase):
    __tablename__ = 'projects'
    project_id = db.Column(
        db.Integer(), nullable=False, primary_key=True, autoincrement=True
    )
    name = db.Column(db.String(50), nullable=False, unique=True)


class ProjectsHistory(SQLBase, ProjectsBase, HistoryMixin):
    __tablename__ = 'projectshistory'
    id = db.Column(
        db.Integer(), nullable=False, primary_key=True, autoincrement=True
    )
    name = db.Column(db.String(50), nullable=False)

    # Foreign key constraint requires special handling.
    @sqlalchemy.ext.declarative.declared_attr
    def project_id(cls):
        return db.Column(
            db.Integer(), db.ForeignKey('projects.project_id'), nullable=False
        )


class ContactEmailsBase(object):
    id = db.Column(
        db.Integer(), nullable=False, primary_key=True, autoincrement=True
    )
    # type can be either "primary" or "secondary". By convention, there should
    # be exactly one primary contact for each project.
    type = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    # index sets the order which contacts are listed in. By convention, the one
    # primary contact should have index 0.
    index = db.Column(db.Integer(), nullable=False)

    # Foreign key constraint requires special handling.
    @sqlalchemy.ext.declarative.declared_attr
    def project_id(cls):
        return db.Column(
            db.Integer(), db.ForeignKey('projects.project_id'), nullable=False
        )


class ContactEmails(SQLBase, ContactEmailsBase):
    __tablename__ = "contactemails"


class ContactEmailsHistory(SQLBase, ContactEmailsBase, HistoryMixin):
    __tablename__ = 'contactemailshistory'


class RolesBase(object):
    id = sqlalchemy.Column(
        sqlalchemy.Integer(), nullable=False, primary_key=True,
        autoincrement=True
    )
    role = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    prereq = db.Column(db.Text(), nullable=True)
    # index sets the order which roles are listed in:
    index = db.Column(db.Integer(), nullable=False)

    # Foreign key constraint requires special handling.
    @sqlalchemy.ext.declarative.declared_attr
    def project_id(cls):
        return db.Column(
            db.Integer(), db.ForeignKey('projects.project_id'), nullable=False
        )


class Roles(SQLBase, RolesBase):
    __tablename__ = "roles"


class RolesHistory(SQLBase, RolesBase, HistoryMixin):
    __tablename__ = 'roleshistory'


class LinksBase(object):
    id = db.Column(
        db.Integer(), nullable=False, primary_key=True,
        autoincrement=True
    )
    link = db.Column(db.Text(), nullable=False)
    # index sets the order which links are listed in:
    index = db.Column(db.Integer(), nullable=False)

    # Foreign key constraint requires special handling.
    @sqlalchemy.ext.declarative.declared_attr
    def project_id(cls):
        return db.Column(
            db.Integer(), db.ForeignKey('projects.project_id'), nullable=False
        )


class Links(SQLBase, LinksBase):
    __tablename__ = "links"


class LinksHistory(SQLBase, LinksBase, HistoryMixin):
    __tablename__ = 'linkshistory'


class CommChannelsBase(object):
    id = db.Column(
        db.Integer(), nullable=False, primary_key=True,
        autoincrement=True
    )
    commchannel = db.Column(db.Text(), nullable=False)
    # index sets the order which comm channels are listed in:
    index = db.Column(db.Integer(), nullable=False)

    # Foreign key constraint requires special handling.
    @sqlalchemy.ext.declarative.declared_attr
    def project_id(cls):
        return db.Column(
            db.Integer(), db.ForeignKey('projects.project_id'), nullable=False
        )


class CommChannels(SQLBase, CommChannelsBase):
    __tablename__ = "commchannels"
    

class CommChannelsHistory(SQLBase, CommChannelsBase, HistoryMixin):
    __tablename__ = 'commchannelshistory'


# Implement schema
SQLBase.metadata.create_all(sqlengine)

# Define data structure to help with history generation:
CLASS_TO_HISTORY_CLASS_MAP = {
    Projects: ProjectsHistory,
    ContactEmails: ContactEmailsHistory,
    Roles: RolesHistory,
    Links: LinksHistory,
    CommChannels: CommChannelsHistory
}
