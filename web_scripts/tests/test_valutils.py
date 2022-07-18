#!/usr/bin/env python

# testutils MUST be imported first to set up test configuration and module
# paths properly!
import testutils

import os
import unittest

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
        os.environ['SSL_CLIENT_S_DN_Email'] = 'rif'
        is_ok, status_messages = valutils.validate_add_permission()
        self.assertTrue(is_ok)
        self.assertEqual(len(status_messages), 0)

    def test_nonmember(self):
        os.environ['SSL_CLIENT_S_DN_Email'] = \
            'this_is_definitely_not_a_valid_kerb'
        is_ok, status_messages = valutils.validate_add_permission()
        self.assertFalse(is_ok)
        self.assertGreaterEqual(len(status_messages), 1)


if __name__ == '__main__':
    unittest.main()
