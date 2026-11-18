#!/usr/bin/env python3
"""Tests for the VFS data stream interface."""

import unittest

from dfvfs.vfs import data_stream

from tests import test_lib as shared_test_lib


class TestFileEntry:
    """Test file entry to determine the size of the default data stream."""

    def __init__(self, size):
        """Initializes a test file entry.

        Args:
          size (int): size of the file entry data.
        """
        super().__init__()
        self.size = size

    def GetExtents(self):
        """Retrieves the extents.

        Returns:
          list[Extent]: the extents of the file entry data.
        """
        return []


class TestNamedDataStream(data_stream.DataStream):
    """Test data stream with an explicit name and size."""

    def __init__(self, file_entry, name, size):
        """Initializes a test named data stream.

        Args:
          file_entry (FileEntry): file entry.
          name (str): name of the data stream.
          size (int): size of the data stream.
        """
        super().__init__(file_entry)
        self._name = name
        self._size = size


class DataStreamTest(shared_test_lib.BaseTestCase):
    """Tests the VFS data stream interface."""

    def testName(self):
        """Test the name property."""
        test_data_stream = data_stream.DataStream(None)
        self.assertEqual(test_data_stream.name, "")

    def testSize(self):
        """Test the size property."""
        # Without a file entry the size defaults to 0.
        test_data_stream = data_stream.DataStream(None)
        self.assertEqual(test_data_stream.size, 0)

        # The default data stream size equals the file entry data size.
        test_data_stream = data_stream.DataStream(TestFileEntry(116))
        self.assertEqual(test_data_stream.size, 116)

        # A named data stream uses its own size instead of the file entry size.
        test_data_stream = TestNamedDataStream(TestFileEntry(116), "named", 32)
        self.assertEqual(test_data_stream.size, 32)

    def testGetExtents(self):
        """Test the GetExtents function."""
        test_data_stream = data_stream.DataStream(None)
        extents = test_data_stream.GetExtents()
        self.assertEqual(extents, [])

    def testIsDefault(self):
        """Test the IsDefault function."""
        test_data_stream = data_stream.DataStream(None)
        result = test_data_stream.IsDefault()
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
