#!/usr/bin/env python3
"""Tests for the VFS file system object interface."""

import unittest

from dfvfs.path import fake_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import data_stream
from dfvfs.vfs import file_system

from tests import test_lib as shared_test_lib


class TestFileEntry:
    """File entry for testing."""

    def __init__(self):
        """Initializes a test file entry."""
        super().__init__()
        self._data_streams = [data_stream.DataStream(self)]
        self.size = 116

    def GetDataStream(self, name, case_sensitive=True):
        """Retrieves a data stream by name.

        Args:
          name (str): name of the data stream.
          case_sensitive (Optional[bool]): True if the name is case sensitive.

        Returns:
          DataStream: a data stream or None if not available.
        """
        # pylint: disable=unused-argument
        for test_data_stream in self._data_streams:
            if test_data_stream.name == name:
                return test_data_stream
        return None


class TestFileSystem(file_system.FileSystem):
    """File system for testing."""

    # pylint: disable=abstract-method

    TYPE_INDICATOR = "test"

    def GetFileEntryByPathSpec(self, path_spec):
        """Retrieves a file entry for a path specification.

        Args:
          path_spec (PathSpec): a path specification.

        Returns:
          FileEntry: a file entry or None if not available.
        """
        return TestFileEntry()


class FileSystemTest(shared_test_lib.BaseTestCase):
    """Tests the VFS file system object interface."""

    def setUp(self):
        """Sets up the needed objects used throughout the test."""
        self._resolver_context = context.Context()

    def testInitialize(self):
        """Test the __init__ function."""
        path_spec = fake_path_spec.FakePathSpec(location="/")

        with self.assertRaises(ValueError):
            file_system.FileSystem(self._resolver_context, path_spec)

    # TODO: add tests for type_indicator property.
    # TODO: add tests for _Close function.
    # TODO: add tests for _Open function.
    # TODO: add tests for BasenamePath function.
    # TODO: add tests for Close function.
    # TODO: add tests for DirnamePath function.
    # TODO: add tests for GetFileObjectByPathSpec function.
    # TODO: add tests for GetPathSegmentAndSuffix function.

    def testGetDataStreamByPathSpec(self):
        """Tests the GetDataStreamByPathSpec function."""
        path_spec = fake_path_spec.FakePathSpec(location="/")
        test_file_system = TestFileSystem(self._resolver_context, path_spec)

        # A path specification without a data_stream attribute resolves to the
        # default data stream instead of raising an error.
        test_data_stream = test_file_system.GetDataStreamByPathSpec(path_spec)
        self.assertIsNotNone(test_data_stream)
        self.assertEqual(test_data_stream.name, "")

        # An explicit empty data_stream name resolves to the default data
        # stream.
        path_spec = fake_path_spec.FakePathSpec(location="/")
        setattr(path_spec, "data_stream", "")
        test_data_stream = test_file_system.GetDataStreamByPathSpec(path_spec)
        self.assertIsNotNone(test_data_stream)
        self.assertEqual(test_data_stream.name, "")

        # A non-existing data stream name results in None.
        path_spec = fake_path_spec.FakePathSpec(location="/")
        setattr(path_spec, "data_stream", "bogus")
        test_data_stream = test_file_system.GetDataStreamByPathSpec(path_spec)
        self.assertIsNone(test_data_stream)

    def testJoinPath(self):
        """Test the join path functionality."""
        path_spec = fake_path_spec.FakePathSpec(location="/")

        test_file_system = TestFileSystem(self._resolver_context, path_spec)

        expected_path = "/test1/test2/test3"

        path = test_file_system.JoinPath(["test1", "test2", "test3"])
        self.assertEqual(path, expected_path)

        path = test_file_system.JoinPath(["/test1", "test2//", "test3/"])
        self.assertEqual(path, expected_path)

        path = test_file_system.JoinPath(["/test1/test2/", "/test3/"])
        self.assertEqual(path, expected_path)

        path = test_file_system.JoinPath(["/test1///test2", "test3"])
        self.assertEqual(path, expected_path)

    # TODO: add tests for Open function.

    def testSplitPath(self):
        """Test the split path functionality."""
        path_spec = fake_path_spec.FakePathSpec(location="/")

        test_file_system = TestFileSystem(self._resolver_context, path_spec)

        expected_path_segments = ["test1", "test2", "test3"]

        path_segments = test_file_system.SplitPath("/test1/test2/test3")
        self.assertEqual(path_segments, expected_path_segments)

        path_segments = test_file_system.SplitPath("/test1/test2/test3/")
        self.assertEqual(path_segments, expected_path_segments)

        path_segments = test_file_system.SplitPath("/test1///test2/test3")
        self.assertEqual(path_segments, expected_path_segments)


if __name__ == "__main__":
    unittest.main()
