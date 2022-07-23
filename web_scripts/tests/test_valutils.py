#!/usr/bin/env python

# testutils MUST be imported first to set up test configuration and module
# paths properly!
import testutils

import os
import unittest

import config
import db
import valutils


class Test_all_unique(unittest.TestCase):
    def test_unique_ignore_case(self):
        vals = ['alpha', 'bravo', 'charlie']
        result = valutils.all_unique(vals, ignore_case=True)
        self.assertTrue(result)

    def test_unique_with_case(self):
        vals = ['alpha', 'ALPHA', 'bravo', 'charlie']
        result = valutils.all_unique(vals, ignore_case=False)
        self.assertTrue(result)

    def test_nonunique_ignore_case(self):
        vals = ['alpha', 'ALPHA', 'bravo', 'charlie']
        result = valutils.all_unique(vals, ignore_case=True)
        self.assertFalse(result)

    def test_nonunique_with_case(self):
        vals = ['alpha', 'bravo', 'bravo', 'charlie']
        result = valutils.all_unique(vals, ignore_case=False)
        self.assertFalse(result)


class Test_validate_add_permission(testutils.EnvironmentOverrideTestCase):
    def test_none(self):
        os.environ.pop('SSL_CLIENT_S_DN_Email', None)
        is_ok, status_messages = valutils.validate_add_permission()
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)

    def test_member(self):
        # rif was memberized in 1991, and this test will need to be revised
        # should they be elected a keyholder.
        os.environ['SSL_CLIENT_S_DN_Email'] = 'rif' + '@mit.edu'
        is_ok, status_messages = valutils.validate_add_permission()
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_nonmember(self):
        os.environ['SSL_CLIENT_S_DN_Email'] = \
            'this_is_definitely_not_a_valid_kerb@mit.edu'
        is_ok, status_messages = valutils.validate_add_permission()
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)


class Test_validate_project_name_text(unittest.TestCase):
    def test_empty(self):
        is_ok, status_messages = valutils.validate_project_name_text('')
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)

    def test_long(self):
        is_ok, status_messages = valutils.validate_project_name_text('A' * 100)
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)

    def test_basic(self):
        is_ok, status_messages = valutils.validate_project_name_text('test')
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)


class Test_validate_project_name_available(testutils.DatabaseWipeTestCase):
    def setUp(self):
        super(Test_validate_project_name_available, self).setUp()

        self.project_info_list = [
            {
                'name': 'test1',
                'description': 'some test description',
                'status': 'active',
                'links': [],
                'comm_channels': [],
                'contacts': [
                    {'email': 'foo@mit.edu', 'type': 'primary', 'index': 0}
                ],
                'roles': []
            }
        ]
        self.initial_approvals = ['approved']
        for project_info, initial_approval in zip(
            self.project_info_list, self.initial_approvals
        ):
            project_info['project_id'] = db.add_project(
                project_info, 'creator', initial_approval=initial_approval
            )
            project_info['approval'] = initial_approval

    def test_available(self):
        is_ok, status_messages = valutils.validate_project_name_available(
            'test2'
        )
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_taken(self):
        is_ok, status_messages = valutils.validate_project_name_available(
            'test1'
        )
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)

    def test_taken_case(self):
        is_ok, status_messages = valutils.validate_project_name_available(
            'TEST1'
        )
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)


class Test_validate_project_name(testutils.DatabaseWipeTestCase):
    def setUp(self):
        super(Test_validate_project_name, self).setUp()

        self.project_info_list = [
            {
                'name': 'test1',
                'description': 'some test description',
                'status': 'active',
                'links': [],
                'comm_channels': [],
                'contacts': [
                    {'email': 'foo@mit.edu', 'type': 'primary', 'index': 0}
                ],
                'roles': []
            },
            {
                'name': 'test2',
                'description': 'some test description',
                'status': 'active',
                'links': [],
                'comm_channels': [],
                'contacts': [
                    {
                        'email': 'this_is_definitely_not_a_valid_kerb@mit.edu',
                        'type': 'primary',
                        'index': 0
                    }
                ],
                'roles': []
            }
        ]
        self.initial_approvals = ['approved', 'approved']
        for project_info, initial_approval in zip(
            self.project_info_list, self.initial_approvals
        ):
            project_info['project_id'] = db.add_project(
                project_info, 'creator', initial_approval=initial_approval
            )
            project_info['approval'] = initial_approval

    def test_empty_no_prev(self):
        is_ok, status_messages = valutils.validate_project_name('')
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)

    def test_available_no_prev(self):
        is_ok, status_messages = valutils.validate_project_name('test3')
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_taken_no_prev(self):
        is_ok, status_messages = valutils.validate_project_name('test1')
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)

    def test_same_with_prev(self):
        is_ok, status_messages = valutils.validate_project_name(
            'test1', previous_name='test1'
        )
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_empty_with_prev(self):
        is_ok, status_messages = valutils.validate_project_name(
            '', previous_name='test1'
        )
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)

    def test_available_with_prev(self):
        is_ok, status_messages = valutils.validate_project_name(
            'test3', previous_name='test1'
        )
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_taken_with_prev(self):
        is_ok, status_messages = valutils.validate_project_name(
            'test2', previous_name='test1'
        )
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)


class Test_validate_project_description(unittest.TestCase):
    def test_empty(self):
        is_ok, status_messages = valutils.validate_project_description('')
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)

    def test_too_short(self):
        is_ok, status_messages = valutils.validate_project_description('word')
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)

    def test_ok(self):
        is_ok, status_messages = valutils.validate_project_description(
            'word word word'
        )
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)


class Test_validate_project_contacts_nonempty(unittest.TestCase):
    def test_empty(self):
        is_ok, status_messages = valutils.validate_project_contacts_nonempty(
            []
        )
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)

    def test_one(self):
        is_ok, status_messages = valutils.validate_project_contacts_nonempty(
            [
                {
                    'email': 'foo@mit.edu',
                    'type': 'primary',
                    'index': 0
                }
            ]
        )
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)


class Test_validate_project_contact_addresses(unittest.TestCase):
    def test_valid(self):
        is_ok, status_messages = valutils.validate_project_contact_addresses(
            [
                {
                    'email': 'foo@mit.edu',
                    'type': 'primary',
                    'index': 0
                },
                {
                    'email': 'foo@bar.mit.edu',
                    'type': 'secondary',
                    'index': 1
                }
            ]
        )
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_too_long(self):
        is_ok, status_messages = valutils.validate_project_contact_addresses(
            [
                {
                    'email': ('A' * 100) + '@mit.edu',
                    'type': 'primary',
                    'index': 0
                }
            ]
        )
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)

    def test_non_mit(self):
        is_ok, status_messages = valutils.validate_project_contact_addresses(
            [
                {
                    'email': 'foo@mit.edu',
                    'type': 'primary',
                    'index': 0
                },
                {
                    'email': 'foo@bar.com',
                    'type': 'secondary',
                    'index': 1
                }
            ]
        )
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)

    def test_no_base_mit(self):
        is_ok, status_messages = valutils.validate_project_contact_addresses(
            [
                {
                    'email': 'foo@bar.mit.edu',
                    'type': 'primary',
                    'index': 0
                }
            ]
        )
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)


class Test_validate_project_contacts_unique(unittest.TestCase):
    def test_unique(self):
        is_ok, status_messages = valutils.validate_project_contacts_unique(
            [
                {
                    'email': 'foo@mit.edu',
                    'type': 'primary',
                    'index': 0
                },
                {
                    'email': 'foo@bar.mit.edu',
                    'type': 'secondary',
                    'index': 1
                }
            ]
        )
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_repeated(self):
        is_ok, status_messages = valutils.validate_project_contacts_unique(
            [
                {
                    'email': 'foo@mit.edu',
                    'type': 'primary',
                    'index': 0
                },
                {
                    'email': 'foo@mit.edu',
                    'type': 'secondary',
                    'index': 1
                }
            ]
        )
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)


class Test_validate_project_contacts(unittest.TestCase):
    def test_empty(self):
        is_ok, status_messages = valutils.validate_project_contacts([])
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)

    def test_valid(self):
        is_ok, status_messages = valutils.validate_project_contacts(
            [
                {
                    'email': 'foo@mit.edu',
                    'type': 'primary',
                    'index': 0
                },
                {
                    'email': 'foo@bar.mit.edu',
                    'type': 'secondary',
                    'index': 1
                }
            ]
        )
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_invalid(self):
        is_ok, status_messages = valutils.validate_project_contacts(
            [
                {
                    'email': 'foo@mit.edu',
                    'type': 'primary',
                    'index': 0
                },
                {
                    'email': 'foo@mit.edu',
                    'type': 'secondary',
                    'index': 1
                }
            ]
        )
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)


class Test_validate_project_role_fields(unittest.TestCase):
    def test_empty(self):
        is_ok, status_messages = valutils.validate_project_role_fields([])
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_valid(self):
        is_ok, status_messages = valutils.validate_project_role_fields(
            [
                {
                    'role': 'foo',
                    'description': 'bar',
                    'prereq': '',
                    'index': 0
                }
            ]
        )
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_name_too_long(self):
        is_ok, status_messages = valutils.validate_project_role_fields(
            [
                {
                    'role': 'A' * 100,
                    'description': 'bar',
                    'prereq': '',
                    'index': 0
                }
            ]
        )
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)

    def test_no_name(self):
        is_ok, status_messages = valutils.validate_project_role_fields(
            [
                {
                    'role': '',
                    'description': 'bar',
                    'prereq': '',
                    'index': 0
                }
            ]
        )
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)

    def test_no_description(self):
        is_ok, status_messages = valutils.validate_project_role_fields(
            [
                {
                    'role': 'A',
                    'description': '',
                    'prereq': '',
                    'index': 0
                }
            ]
        )
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)


class Test_validate_project_roles_unique(unittest.TestCase):
    def test_empty(self):
        is_ok, status_messages = valutils.validate_project_roles_unique([])
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_valid(self):
        is_ok, status_messages = valutils.validate_project_roles_unique(
            [
                {
                    'role': 'A',
                    'description': 'foo',
                    'prereq': '',
                    'index': 0
                },
                {
                    'role': 'B',
                    'description': 'bar',
                    'prereq': '',
                    'index': 1
                }
            ]
        )
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_invalid(self):
        is_ok, status_messages = valutils.validate_project_roles_unique(
            [
                {
                    'role': 'A',
                    'description': 'foo',
                    'prereq': '',
                    'index': 0
                },
                {
                    'role': 'A',
                    'description': 'bar',
                    'prereq': '',
                    'index': 1
                }
            ]
        )
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)


class Test_validate_project_roles(unittest.TestCase):
    def test_empty(self):
        is_ok, status_messages = valutils.validate_project_roles([])
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_valid(self):
        is_ok, status_messages = valutils.validate_project_roles(
            [
                {
                    'role': 'A',
                    'description': 'foo',
                    'prereq': '',
                    'index': 0
                },
                {
                    'role': 'B',
                    'description': 'bar',
                    'prereq': '',
                    'index': 1
                }
            ]
        )
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_invalid(self):
        is_ok, status_messages = valutils.validate_project_roles(
            [
                {
                    'role': 'A',
                    'description': 'foo',
                    'prereq': '',
                    'index': 0
                },
                {
                    'role': 'A',
                    'description': '',
                    'prereq': '',
                    'index': 1
                }
            ]
        )
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)


class Test_validate_project_links(unittest.TestCase):
    def test_empty(self):
        is_ok, status_messages = valutils.validate_project_links([])
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_valid(self):
        is_ok, status_messages = valutils.validate_project_links(
            [
                {
                    'link': 'mit.edu',
                    'anchortext': '',
                    'index': 0
                },
                {
                    'link': 'csail.mit.edu',
                    'anchortext': 'foo bar baz',
                    'index': 1
                }
            ]
        )
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_invalid(self):
        is_ok, status_messages = valutils.validate_project_links(
            [
                {
                    'link': 'mit.edu',
                    'anchortext': '',
                    'index': 0
                },
                {
                    'link': 'mit.edu',
                    'anchortext': 'foo bar baz',
                    'index': 1
                }
            ]
        )
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)


class Test_validate_project_comm_channels(unittest.TestCase):
    def test_empty(self):
        is_ok, status_messages = valutils.validate_project_comm_channels([])
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_valid(self):
        is_ok, status_messages = valutils.validate_project_comm_channels(
            [
                {
                    'commchannel': 'mattermost',
                    'index': 0
                },
                {
                    'commchannel': 'carrier pigeon',
                    'index': 1
                }
            ]
        )
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_invalid(self):
        is_ok, status_messages = valutils.validate_project_comm_channels(
            [
                {
                    'commchannel': 'mattermost',
                    'index': 0
                },
                {
                    'commchannel': 'mattermost',
                    'index': 1
                }
            ]
        )
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)


class Test_validate_project_info(testutils.DatabaseWipeTestCase):
    def setUp(self):
        super(Test_validate_project_info, self).setUp()

        self.project_info_list = [
            {
                'name': 'test1',
                'description': 'some test description',
                'status': 'active',
                'links': [],
                'comm_channels': [],
                'contacts': [
                    {'email': 'foo@mit.edu', 'type': 'primary', 'index': 0}
                ],
                'roles': []
            },
            {
                'name': 'test2',
                'description': 'some test description',
                'status': 'active',
                'links': [],
                'comm_channels': [],
                'contacts': [
                    {
                        'email': 'this_is_definitely_not_a_valid_kerb@mit.edu',
                        'type': 'primary',
                        'index': 0
                    }
                ],
                'roles': []
            }
        ]
        self.initial_approvals = ['approved', 'approved']
        for project_info, initial_approval in zip(
            self.project_info_list, self.initial_approvals
        ):
            project_info['project_id'] = db.add_project(
                project_info, 'creator', initial_approval=initial_approval
            )
            project_info['approval'] = initial_approval

    def test_ok_no_previous(self):
        project_info = {
            'name': 'test3',
            'description': 'some test description',
            'status': 'active',
            'links': [],
            'comm_channels': [],
            'contacts': [
                {
                    'email': 'foo@mit.edu',
                    'type': 'primary',
                    'index': 0
                }
            ],
            'roles': []
        }
        is_ok, status_messages = valutils.validate_project_info(project_info)
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_invalid_no_previous(self):
        project_info = {
            'name': 'test1',
            'description': 'some test description',
            'status': 'active',
            'links': [],
            'comm_channels': [],
            'contacts': [
                {
                    'email': 'foo@mit.edu',
                    'type': 'primary',
                    'index': 0
                }
            ],
            'roles': []
        }
        is_ok, status_messages = valutils.validate_project_info(project_info)
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)

    def test_ok_with_previous(self):
        project_info = {
            'name': 'test1',
            'description': 'some test description',
            'status': 'active',
            'links': [],
            'comm_channels': [],
            'contacts': [
                {
                    'email': 'foo@mit.edu',
                    'type': 'primary',
                    'index': 0
                }
            ],
            'roles': []
        }
        is_ok, status_messages = valutils.validate_project_info(
            project_info, previous_name='test1'
        )
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_invalid_with_previous(self):
        project_info = {
            'name': 'test1',
            'description': 'some test description',
            'status': 'active',
            'links': [],
            'comm_channels': [],
            'contacts': [
                {
                    'email': 'foo@mit.edu',
                    'type': 'primary',
                    'index': 0
                }
            ],
            'roles': []
        }
        is_ok, status_messages = valutils.validate_project_info(
            project_info, previous_name='test2'
        )
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)


class Test_validate_add_project(
    testutils.EnvironmentOverrideDatabaseWipeTestCase
):
    def setUp(self):
        super(Test_validate_add_project, self).setUp()

        self.project_info_list = [
            {
                'name': 'test1',
                'description': 'some test description',
                'status': 'active',
                'links': [],
                'comm_channels': [],
                'contacts': [
                    {'email': 'foo@mit.edu', 'type': 'primary', 'index': 0}
                ],
                'roles': []
            },
            {
                'name': 'test2',
                'description': 'some test description',
                'status': 'active',
                'links': [],
                'comm_channels': [],
                'contacts': [
                    {
                        'email': 'this_is_definitely_not_a_valid_kerb@mit.edu',
                        'type': 'primary',
                        'index': 0
                    }
                ],
                'roles': []
            }
        ]
        self.initial_approvals = ['approved', 'approved']
        for project_info, initial_approval in zip(
            self.project_info_list, self.initial_approvals
        ):
            project_info['project_id'] = db.add_project(
                project_info, 'creator', initial_approval=initial_approval
            )
            project_info['approval'] = initial_approval

    def test_valid(self):
        os.environ['SSL_CLIENT_S_DN_Email'] = 'rif' + '@mit.edu'
        project_info = {
            'name': 'test3',
            'description': 'some test description',
            'status': 'active',
            'links': [],
            'comm_channels': [],
            'contacts': [
                {
                    'email': 'foo@mit.edu',
                    'type': 'primary',
                    'index': 0
                }
            ],
            'roles': []
        }
        is_ok, status_messages = valutils.validate_add_project(project_info)
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_invalid(self):
        os.environ.pop('SSL_CLIENT_S_DN_Email', None)
        project_info = {
            'name': 'test3',
            'description': 'some test description',
            'status': 'active',
            'links': [],
            'comm_channels': [],
            'contacts': [
                {
                    'email': 'foo@mit.edu',
                    'type': 'primary',
                    'index': 0
                }
            ],
            'roles': []
        }
        is_ok, status_messages = valutils.validate_add_project(project_info)
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)


class Test_validate_edit_permission(
    testutils.EnvironmentOverrideDatabaseWipeTestCase
):
    def setUp(self):
        super(Test_validate_edit_permission, self).setUp()

        self.project_info_list = [
            {
                'name': 'test1',
                'description': 'some test description',
                'status': 'active',
                'links': [],
                'comm_channels': [],
                'contacts': [
                    {'email': 'foo@mit.edu', 'type': 'primary', 'index': 0}
                ],
                'roles': []
            }
        ]
        self.initial_approvals = ['approved', 'approved']
        for project_info, initial_approval in zip(
            self.project_info_list, self.initial_approvals
        ):
            project_info['project_id'] = db.add_project(
                project_info, 'creator', initial_approval=initial_approval
            )
            project_info['approval'] = initial_approval

    def test_none(self):
        os.environ.pop('SSL_CLIENT_S_DN_Email', None)
        project_id = db.get_project_id('test1')
        is_ok, status_messages = valutils.validate_edit_permission(project_id)
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)

    def test_contact(self):
        os.environ['SSL_CLIENT_S_DN_Email'] = 'foo@mit.edu'
        project_id = db.get_project_id('test1')
        is_ok, status_messages = valutils.validate_edit_permission(project_id)
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_noncontact(self):
        os.environ['SSL_CLIENT_S_DN_Email'] = \
            'this_is_definitely_not_a_valid_kerb@mit.edu'
        project_id = db.get_project_id('test1')
        is_ok, status_messages = valutils.validate_edit_permission(project_id)
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)


class Test_validate_edit_project(
    testutils.EnvironmentOverrideDatabaseWipeTestCase
):
    def setUp(self):
        super(Test_validate_edit_project, self).setUp()

        self.project_info_list = [
            {
                'name': 'test1',
                'description': 'some test description',
                'status': 'active',
                'links': [],
                'comm_channels': [],
                'contacts': [
                    {'email': 'foo@mit.edu', 'type': 'primary', 'index': 0}
                ],
                'roles': []
            },
            {
                'name': 'test2',
                'description': 'some test description',
                'status': 'active',
                'links': [],
                'comm_channels': [],
                'contacts': [
                    {
                        'email': 'this_is_definitely_not_a_valid_kerb@mit.edu',
                        'type': 'primary',
                        'index': 0
                    }
                ],
                'roles': []
            }
        ]
        self.initial_approvals = ['approved', 'approved']
        for project_info, initial_approval in zip(
            self.project_info_list, self.initial_approvals
        ):
            project_info['project_id'] = db.add_project(
                project_info, 'creator', initial_approval=initial_approval
            )
            project_info['approval'] = initial_approval

    def test_none(self):
        os.environ.pop('SSL_CLIENT_S_DN_Email', None)
        project_info = {
            'name': 'test3',
            'description': 'some test description',
            'status': 'active',
            'links': [],
            'comm_channels': [],
            'contacts': [
                {
                    'email': 'foo@mit.edu',
                    'type': 'primary',
                    'index': 0
                }
            ],
            'roles': []
        }
        project_id = db.get_project_id('test1')
        is_ok, status_messages = valutils.validate_edit_project(
            project_info, project_id
        )
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)

    def test_valid_same_name(self):
        os.environ['SSL_CLIENT_S_DN_Email'] = 'foo@mit.edu'
        project_info = {
            'name': 'test1',
            'description': 'some test description',
            'status': 'active',
            'links': [],
            'comm_channels': [],
            'contacts': [
                {
                    'email': 'foo@mit.edu',
                    'type': 'primary',
                    'index': 0
                }
            ],
            'roles': []
        }
        project_id = db.get_project_id('test1')
        is_ok, status_messages = valutils.validate_edit_project(
            project_info, project_id
        )
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_valid_new_name(self):
        os.environ['SSL_CLIENT_S_DN_Email'] = 'foo@mit.edu'
        project_info = {
            'name': 'test3',
            'description': 'some test description',
            'status': 'active',
            'links': [],
            'comm_channels': [],
            'contacts': [
                {
                    'email': 'foo@mit.edu',
                    'type': 'primary',
                    'index': 0
                }
            ],
            'roles': []
        }
        project_id = db.get_project_id('test1')
        is_ok, status_messages = valutils.validate_edit_project(
            project_info, project_id
        )
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)


class Test_validate_approval_permission(testutils.EnvironmentOverrideTestCase):
    def test_none(self):
        os.environ.pop('SSL_CLIENT_S_DN_Email', None)
        is_ok, status_messages = valutils.validate_approval_permission()
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)

    def test_non_approver(self):
        os.environ['SSL_CLIENT_S_DN_Email'] = \
            'this_is_definitely_not_a_valid_kerb@mit.edu'
        is_ok, status_messages = valutils.validate_approval_permission()
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)

    def test_admin(self):
        if len(config.ADMIN_USERS) > 0:
            os.environ['SSL_CLIENT_S_DN_Email'] = \
                config.ADMIN_USERS[0] + '@mit.edu'
            is_ok, status_messages = valutils.validate_approval_permission()
            self.assertTrue(is_ok)
            self.assertEqual(len(status_messages), 0)

    def test_approver(self):
        if len(config.APPROVER_USERS) > 0:
            os.environ['SSL_CLIENT_S_DN_Email'] = \
                config.APPROVER_USERS[0] + '@mit.edu'
            is_ok, status_messages = valutils.validate_approval_permission()
            self.assertTrue(is_ok)
            self.assertEqual(len(status_messages), 0)


class Test_validate_approval_action(unittest.TestCase):
    def test_approved(self):
        is_ok, status_messages = valutils.validate_approval_action('approved')
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_rejected(self):
        is_ok, status_messages = valutils.validate_approval_action('rejected')
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_invalid(self):
        is_ok, status_messages = valutils.validate_approval_action('invalid')
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)


if __name__ == '__main__':
    unittest.main()
