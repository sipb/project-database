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


class Projects(SQLBase):
    __tablename__ = "projects"
    project_id = db.Column(
        db.Integer(), nullable=False, primary_key=True, autoincrement=True
    )
    name = db.Column(db.String(50), nullable=False, unique=True)
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


class ProjectsHistory(SQLBase):
    __tablename__ = 'projectshistory'
    id = db.Column(
        db.Integer(), nullable=False, primary_key=True, autoincrement=True
    )
    project_id = db.Column(
        db.Integer(), db.ForeignKey('projects.project_id'), nullable=False
    )
    name = db.Column(db.String(50), nullable=False, unique=True)
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

    author = db.Column(db.String(50), nullable=False)
    # action can be 'create', 'update', 'delete'
    action = db.Column(db.String(25), nullable=False)
    revision_id = db.Column(db.Integer(), nullable=False)
    timestamp = db.Column(
        db.TIMESTAMP, nullable=False, server_default=db.func.now()
    )


class ContactEmails(SQLBase):
    __tablename__ = "contactemails"
    id = db.Column(
        db.Integer(), nullable=False, primary_key=True,
        autoincrement=True
    )
    project_id = db.Column(
        db.Integer(), db.ForeignKey('projects.project_id'), nullable=False
    )
    # type can be either "primary" or "secondary". By convention, there should
    # be exactly one primary contact for each project.
    type = db.Column(
        db.String(25), nullable=False
    )
    email = db.Column(db.String(50), nullable=False)
    # index sets the order which contacts are listed in. By convention, the one
    # primary contact should have index 0.
    index = db.Column(db.Integer(), nullable=False)


class Roles(SQLBase):
    __tablename__ = "roles"
    id = sqlalchemy.Column(
        sqlalchemy.Integer(), nullable=False, primary_key=True,
        autoincrement=True
    )
    project_id = db.Column(
        db.Integer(), db.ForeignKey('projects.project_id'), nullable=False
    )
    role = db.Column(
        db.String(50), nullable=False
    )
    description = db.Column(db.Text(), nullable=False)
    prereq = db.Column(db.Text(), nullable=True)
    # index sets the order which roles are listed in:
    index = db.Column(db.Integer(), nullable=False)
    

class Links(SQLBase):
    __tablename__ = "links"
    id = sqlalchemy.Column(
        sqlalchemy.Integer(), nullable=False, primary_key=True,
        autoincrement=True
    )
    project_id = db.Column(
        db.Integer(), db.ForeignKey('projects.project_id'), nullable=False
    )
    link = db.Column(db.Text(), nullable=False)
    # index sets the order which links are listed in:
    index = db.Column(db.Integer(), nullable=False)


class CommChannels(SQLBase):
    __tablename__ = "commchannels"
    id = sqlalchemy.Column(
        sqlalchemy.Integer(), nullable=False, primary_key=True,
        autoincrement=True
    )
    project_id = db.Column(
        db.Integer(), db.ForeignKey('projects.project_id'), nullable=False
    )
    commchannel = db.Column(db.Text(), nullable=False)
    # index sets the order which comm channels are listed in:
    index = db.Column(db.Integer(), nullable=False)


# Implement schema
SQLBase.metadata.create_all(sqlengine)
