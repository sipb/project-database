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


class ContactEmails(SQLBase):
    __tablename__ = "contactemails"
    id = sqlalchemy.Column(
        sqlalchemy.Integer(), nullable=False, primary_key=True,
        autoincrement=True
    )
    project_id = db.Column(
        db.Integer(), db.ForeignKey('projects.project_id'), nullable=False
    )
    type = db.Column(
        db.String(25), nullable=False
    )  # Can be either "primary" or "secondary"
    email = db.Column(db.String(50), nullable=False)


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


# Implement schema
SQLBase.metadata.create_all(sqlengine)
