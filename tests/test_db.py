# testutils MUST be imported first to set up test configuration properly!

import testutils

from project_database.models import db, schema

PROJECT_INFO = {
    "name": "SIPB Minecraft",
    "status": "active",
    "description": "Virtual MIT in a Minecraft server!",
    "links": [{"link": "https://sipb.mit.edu/", "index": 0}],
    "comm_channels": [{"commchannel": "sipb-hwops@mit.edu", "index": 0}],
    "contacts": [{"email": "foo@mit.edu", "type": "primary", "index": 0}],
    "roles": [],
}

PROJECT_MOD = {
    "name": "SIPB Takes Over the World",
    "status": "active",
    "description": "April Fools",
}

CONTACTS = [
    {
        "type": "primary",
        "email": "you-fools@mit.edu",
        "index": 0,
    },
    {
        "type": "secondary",
        "email": "ec-discuss-never@mit.edu",
        "index": 1,
    },
]

ROLES = [
    {
        "role": "Support Tech",
        "description": (
            "get familiar with MIT's and SIPB's computing infrastructure by "
            "helping answer user questions and approve user requests."
        ),
        # missing prereq
        "index": 0,
    },
    {
        "role": "Cluster Tech",
        "description": (
            "help design, implement, test, and review SIPB's cluster "
            "management software."
        ),
        "prereq": (
            "previous programming experience in any statically typed language, "
            "knowledge of Python and Go or ability to independently learn them, "
            "6.033-level understanding of computer systems, experience with Git, "
            "experience with Linux"
        ),
        "index": 1,
    },
]

LINKS = [
    {"link": "https://sipb.mit.edu/", "index": 0},
    {"link": "https://hwops.mit.edu/", "index": 1},
]

COMMS = [{"commchannel": "sipb-hwops@mit.edu", "index": 0}]

UPDATE_PROJECT_INFO = {
    "name": "myproject",
    "description": "something something something",
    "status": "active",
    "links": [{"link": "http://link.com", "index": 0}],
    "comm_channels": [{"commchannel": "sipb-hwops@mit.edu", "index": 0}],
    "contacts": [{"email": "markchil@mit.edu", "type": "primary", "index": 0}],
    "roles": [
        {"role": "support tech", "description": "do stuff", "prereq": None, "index": 0}
    ],
}


def strip_internal_fields(rows):
    """Strip the internal database fields (i.e. the row ID and project ID)
    from the given rows, returning copies which may be compared with
    user-provided info.

    Parameters
    ----------
    rows : list of dict
        The rows to strip.

    Returns
    -------
    stripped_rows : list of dict
        The stripped rows.
    """
    return [
        {key: val for key, val in row.items() if key not in ("id", "project_id")}
        for row in rows
    ]


class Test_add_project(testutils.DatabaseEmptyTestCase):
    def test_add_and_get(self):
        project_id = db.add_project(PROJECT_INFO, "creator")
        self.assertTrue(project_id is not None)

        project_info = db.get_all_info_for_project(project_id)
        self.assertEqual(project_info["name"], "SIPB Minecraft")
        self.assertEqual(project_info["status"], "active")
        self.assertEqual(
            project_info["description"], "Virtual MIT in a Minecraft server!"
        )
        self.assertEqual(
            strip_internal_fields(project_info["contacts"]),
            [{"email": "foo@mit.edu", "type": "primary", "index": 0}],
        )
        self.assertEqual(
            strip_internal_fields(project_info["links"]),
            [{"link": "https://sipb.mit.edu/", "anchortext": None, "index": 0}],
        )
        self.assertEqual(
            strip_internal_fields(project_info["comm_channels"]),
            [{"commchannel": "sipb-hwops@mit.edu", "index": 0}],
        )

    def test_get_project_id(self):
        self.assertTrue(db.get_project_id("SIPB Minecraft") is None)
        project_id = db.add_project(PROJECT_INFO, "creator")
        self.assertEqual(db.get_project_id("SIPB Minecraft"), project_id)
        self.assertEqual(db.get_project_id("SIPB MINECRAFT"), project_id)
        self.assertTrue(db.get_project_id("nonexistent") is None)

    def test_duplicate_name(self):
        db.add_project(PROJECT_INFO, "creator")
        with self.assertRaises(ValueError):
            db.add_project(PROJECT_INFO, "creator")


class Test_get_all_projects(testutils.DatabaseEmptyTestCase):
    def test_empty(self):
        self.assertEqual(db.get_all_projects(), [])

    def test_populated(self):
        db.add_project(PROJECT_INFO, "creator")
        projects = db.get_all_projects()
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].name, "SIPB Minecraft")


class Test_add_project_metadata(testutils.DatabaseEmptyTestCase):
    def test_add(self):
        project_id = db.add_project_metadata(
            {
                "name": "test1",
                "status": "active",
                "description": "that is all folks",
                "creator": "creator",
                "approval": "approved",
            }
        )
        schema.session.commit()
        self.assertEqual(db.get_project_id("test1"), project_id)

        self.assertEqual(len(db.get_all_projects()), 1)


class Test_update_project_contacts(testutils.DatabaseEmptyTestCase):
    def test_update(self):
        project_id = db.add_project(PROJECT_INFO, "creator")

        db.update_project_contacts(project_id, CONTACTS, "editor", 1)
        schema.session.commit()

        self.assertEqual(strip_internal_fields(db.get_contacts(project_id)), CONTACTS)


class Test_add_project_roles(testutils.DatabaseEmptyTestCase):
    def test_add(self):
        project_id = db.add_project(PROJECT_INFO, "creator")

        roles = db.add_project_roles(project_id, ROLES, "creator")

        expected_roles = [role.copy() for role in ROLES]
        expected_roles[0]["prereq"] = None
        self.assertEqual(strip_internal_fields(roles), expected_roles)


class Test_update_project_links(testutils.DatabaseEmptyTestCase):
    def test_update(self):
        project_id = db.add_project(PROJECT_INFO, "creator")

        db.update_project_links(project_id, LINKS, "editor", 1)
        schema.session.commit()

        expected_links = [link.copy() for link in LINKS]
        for link in expected_links:
            link["anchortext"] = None
        self.assertEqual(
            strip_internal_fields(db.get_links(project_id)), expected_links
        )


class Test_add_project_comms(testutils.DatabaseEmptyTestCase):
    def test_add(self):
        project_info = dict(PROJECT_INFO, comm_channels=[])
        project_id = db.add_project(project_info, "creator")

        comms = db.add_project_comms(project_id, COMMS, "creator")

        self.assertEqual(strip_internal_fields(comms), COMMS)


class Test_update_project_metadata(testutils.DatabaseEmptyTestCase):
    def test_update(self):
        project_id = db.add_project(PROJECT_INFO, "creator")

        db.update_project_metadata(project_id, PROJECT_MOD, "editor")
        schema.session.commit()

        project_info = db.get_all_info_for_project(project_id)
        self.assertEqual(project_info["name"], "SIPB Takes Over the World")
        self.assertEqual(project_info["description"], "April Fools")


class Test_update_project(testutils.DatabaseEmptyTestCase):
    def test_update(self):
        project_id = db.add_project(PROJECT_INFO, "creator")

        original_project = db.update_project(UPDATE_PROJECT_INFO, project_id, "huydai")

        # The update returns the pre-update project info:
        self.assertEqual(original_project["name"], "SIPB Minecraft")

        project_info = db.get_all_info_for_project(project_id)
        self.assertEqual(project_info["name"], "myproject")
        self.assertEqual(project_info["description"], "something something something")
        self.assertEqual(
            strip_internal_fields(project_info["contacts"]),
            [{"email": "markchil@mit.edu", "type": "primary", "index": 0}],
        )
        self.assertEqual(
            strip_internal_fields(project_info["links"]),
            [{"link": "http://link.com", "anchortext": None, "index": 0}],
        )
        self.assertEqual(
            strip_internal_fields(project_info["roles"]),
            [
                {
                    "role": "support tech",
                    "description": "do stuff",
                    "prereq": None,
                    "index": 0,
                }
            ],
        )

    def test_update_nonexistent(self):
        with self.assertRaises(ValueError):
            db.update_project(UPDATE_PROJECT_INFO, -1, "huydai")


class Test_approval(testutils.DatabaseEmptyTestCase):
    def test_approve(self):
        project_id = db.add_project(PROJECT_INFO, "creator")
        self.assertEqual(
            db.get_project_approval_status(project_id), "awaiting_approval"
        )

        db.approve_project(PROJECT_INFO, project_id, "huydai", "it is good")
        self.assertEqual(db.get_project_approval_status(project_id), "approved")

    def test_reject(self):
        project_id = db.add_project(PROJECT_INFO, "creator")
        self.assertEqual(
            db.get_project_approval_status(project_id), "awaiting_approval"
        )

        db.reject_project(PROJECT_INFO, project_id, "huydai", "it is bad")
        self.assertEqual(db.get_project_approval_status(project_id), "rejected")
