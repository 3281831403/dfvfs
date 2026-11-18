#!/usr/bin/env python3
"""Tests for the serializer object implementation using JSON."""

import os
import unittest

from dfvfs.path import cs_path_spec
from dfvfs.path import encrypted_stream_path_spec
from dfvfs.path import gpt_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import tsk_partition_path_spec
from dfvfs.path import tsk_path_spec
from dfvfs.path import vshadow_path_spec
from dfvfs.serializer import json_serializer as serializer

from tests import test_lib as shared_test_lib


class JsonPathSpecSerializerTest(shared_test_lib.BaseTestCase):
    """Tests for the JSON path specification serializer."""

    def setUp(self):
        """Sets up the needed objects used throughout the test."""
        test_file = self._GetTestFilePath(["ext2.qcow2"])
        self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
        self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=self._os_path_spec)
        self._vshadow_path_spec = vshadow_path_spec.VShadowPathSpec(
            store_index=1, parent=self._qcow_path_spec
        )
        self._tsk_path_spec = tsk_path_spec.TSKPathSpec(
            inode=16,
            location="/a_directory/another_file",
            parent=self._vshadow_path_spec,
        )

        self._tsk_path_spec_dict = {
            "inode": 16,
            "location": "/a_directory/another_file",
            "parent": {
                "store_index": 1,
                "parent": {"parent": {"location": os.path.abspath(test_file)}},
            },
        }

    def testReadAndWriteSerialized(self):
        """Test the ReadSerialized and WriteSerialized function."""
        serialized_path_spec = serializer.JsonPathSpecSerializer.WriteSerialized(
            self._tsk_path_spec
        )

        self.assertIsNotNone(serialized_path_spec)

        path_spec = serializer.JsonPathSpecSerializer.ReadSerialized(
            serialized_path_spec
        )

        self.assertIsNotNone(path_spec)

        path_spec_dict = path_spec.CopyToDict()
        self.assertEqual(
            sorted(path_spec_dict.items()), sorted(self._tsk_path_spec_dict.items())
        )

    def _TestRoundTripIdentity(self, path_spec):
        """Tests that a path specification survives a serialization round-trip.

        Args:
          path_spec (PathSpec): path specification.
        """
        serialized_path_spec = serializer.JsonPathSpecSerializer.WriteSerialized(
            path_spec
        )

        self.assertIsNotNone(serialized_path_spec)

        deserialized_path_spec = serializer.JsonPathSpecSerializer.ReadSerialized(
            serialized_path_spec
        )

        self.assertIsNotNone(deserialized_path_spec)
        self.assertEqual(deserialized_path_spec, path_spec)
        self.assertEqual(deserialized_path_spec.comparable, path_spec.comparable)
        self.assertEqual(hash(deserialized_path_spec), hash(path_spec))
        self.assertEqual(
            sorted(deserialized_path_spec.CopyToDict().items()),
            sorted(path_spec.CopyToDict().items()),
        )

    def testGPTPathSpecRoundTrip(self):
        """Tests that the GPT entry index survives a round-trip."""
        gpt_path_spec_object = gpt_path_spec.GPTPathSpec(
            entry_index=2, location="/gpt3", parent=self._os_path_spec
        )

        self._TestRoundTripIdentity(gpt_path_spec_object)

    def testTSKPartitionPathSpecRoundTrip(self):
        """Tests that the TSK partition sector size survives a round-trip."""
        tsk_partition_path_spec_object = tsk_partition_path_spec.TSKPartitionPathSpec(
            location="/", part_index=1, sector_size=2048, parent=self._os_path_spec
        )

        self._TestRoundTripIdentity(tsk_partition_path_spec_object)

    def testCSPathSpecRoundTrip(self):
        """Tests that the encrypted root plist survives a round-trip."""
        cs_path_spec_object = cs_path_spec.CSPathSpec(
            encrypted_root_plist="/EncryptedRoot.plist.wipekey",
            location="/cs1",
            parent=self._os_path_spec,
        )

        self._TestRoundTripIdentity(cs_path_spec_object)

    def testEncryptedStreamPathSpecRoundTrip(self):
        """Tests that key and initialization vector bytes survive a round-trip."""
        encrypted_stream_path_spec_object = (
            encrypted_stream_path_spec.EncryptedStreamPathSpec(
                cipher_mode="aes-cbc",
                encryption_method="aes",
                initialization_vector=b"\x01\x02\x03\x04",
                key=b"\xde\xad\xbe\xef" * 8,
                parent=self._os_path_spec,
            )
        )

        self._TestRoundTripIdentity(encrypted_stream_path_spec_object)

        serialized_path_spec = serializer.JsonPathSpecSerializer.WriteSerialized(
            encrypted_stream_path_spec_object
        )
        deserialized_path_spec = serializer.JsonPathSpecSerializer.ReadSerialized(
            serialized_path_spec
        )

        self.assertIsInstance(deserialized_path_spec.key, bytes)
        self.assertIsInstance(deserialized_path_spec.initialization_vector, bytes)


if __name__ == "__main__":
    unittest.main()
