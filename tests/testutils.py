# NOTE: when making a test script, `import testutils` should be the very first
# line in your test script. This ensures that the special handshake to put the
# database in test mode gets run before any other modules get imported.

# Set the test mode flag:
import os

os.environ["PROJECTS_DATABASE_MODE"] = "test"

import unittest

from project_database.models import db, schema

# Ensure that we are actually in test mode (i.e. not pointed at the real DB):
assert schema.MODE == "test"


def drop_test_projects():
    """Empty all of the tables in the database."""
    assert schema.MODE == "test"

    # NOTE: this is done with .delete() rather than drop_all() because the
    # latter was found to be unacceptably slow. This method will need to be
    # updated if the schema ever changes.
    schema.session.query(schema.ProjectsHistory).delete()
    schema.session.query(schema.ContactEmails).delete()
    schema.session.query(schema.ContactEmailsHistory).delete()
    schema.session.query(schema.Roles).delete()
    schema.session.query(schema.RolesHistory).delete()
    schema.session.query(schema.Links).delete()
    schema.session.query(schema.LinksHistory).delete()
    schema.session.query(schema.CommChannels).delete()
    schema.session.query(schema.CommChannelsHistory).delete()

    schema.session.query(schema.Projects).delete()

    schema.session.commit()


class DatabaseWipeTestCase(unittest.TestCase):
    """Test fixture which wipes the database before each test, populates it
    with test entries, then wipes it again after the test.
    """

    def setUp(self):
        drop_test_projects()

        self.project_info_list = [
            {
                "name": "test1",
                "description": "some test description",
                "status": "active",
                "links": [],
                "comm_channels": [],
                "contacts": [{"email": "foo@mit.edu", "type": "primary", "index": 0}],
                "roles": [],
            },
            {
                "name": "test2",
                "description": "some test description",
                "status": "active",
                "links": [],
                "comm_channels": [],
                "contacts": [
                    {
                        "email": "this_is_definitely_not_a_valid_kerb@mit.edu",
                        "type": "primary",
                        "index": 0,
                    }
                ],
                "roles": [],
            },
        ]
        self.initial_approvals = ["awaiting_approval", "approved"]
        for project_info, initial_approval in zip(
            self.project_info_list, self.initial_approvals
        ):
            project_info["project_id"] = db.add_project(
                project_info, "creator", initial_approval=initial_approval
            )
            project_info["approval"] = initial_approval

    def tearDown(self):
        drop_test_projects()


class DatabaseEmptyTestCase(unittest.TestCase):
    """Test fixture which wipes the database before each test, without
    populating it with any test entries.
    """

    def setUp(self):
        drop_test_projects()

    def tearDown(self):
        drop_test_projects()
