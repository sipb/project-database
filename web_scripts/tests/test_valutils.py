#!/usr/bin/env python

# testutils MUST be imported first to set up test configuration and module
# paths properly!
import testutils

import os
import unittest

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
        os.environ['SSL_CLIENT_S_DN_Email'] = 'rif@mit.edu'
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
            {
                'email': 'foo@mit.edu',
                'type': 'primary',
                'index': 0
            }
        )
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)


if __name__ == '__main__':
    unittest.main()
