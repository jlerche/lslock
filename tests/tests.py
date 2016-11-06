import unittest
from lslock_test import compare_dicts, make_dir
from lslock import get_inode_and_pid
import unittest.mock as mock
from unittest.mock import patch


class TestLslockTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_compare_dict_equal_dicts_should_be_true(self):
        dict1 = {'foo': [1, 2]}
        dict2 = {'foo': [1, 2]}
        check = compare_dicts(dict1, dict2) and compare_dicts(dict2, dict1)
        self.assertEqual(check, True)

    def test_compare_dict_unequal_dicts_should_be_false(self):
        dict1 = {'foo': [1, 2]}
        dict2 = {'foo': [1, 2], 'bar': [1]}
        check = compare_dicts(dict1, dict2) and compare_dicts(dict2, dict1)
        self.assertNotEqual(check, True)

    @mock.patch('os.path.exists')
    def test_make_dir_should_check_if_exists(self, mock_make_dir):
        path = '/any/path'
        make_dir(path)
        mock_make_dir.assert_called_once_with(path)


class TestLslock(unittest.TestCase):

    def test_get_inode_and_pid_return_tuple(self):
        line = '1: POSIX  ADVISORY  WRITE 972 00:12:630 0 EOF'
        inode, pid = get_inode_and_pid(line)
        self.assertEqual((inode, pid), ('630', '972'))







if __name__ == '__main__':
    unittest.main()
