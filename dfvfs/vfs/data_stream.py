"""The Virtual File System (VFS) data stream interface."""


class DataStream:
    """Data stream interface."""

    def __init__(self, file_entry):
        """Initializes the data stream.

        Args:
          file_entry (FileEntry): file entry.
        """
        super().__init__()
        self._file_entry = file_entry
        self._name = ""
        self._size = 0

    @property
    def name(self):
        """str: name."""
        return self._name

    @property
    def size(self):
        """int: size."""
        # The default data stream contains the data of the file entry, its
        # size therefore equals the size of the file entry. Named data streams
        # store their own size in self._size.
        if not self._name and self._file_entry:
            return self._file_entry.size
        return self._size

    def GetExtents(self):
        """Retrieves the extents.

        Returns:
          list[Extent]: the extents of the data stream.
        """
        if self._file_entry:
            return self._file_entry.GetExtents()
        return []

    def IsDefault(self):
        """Determines if the data stream is the default data stream.

        Returns:
          bool: True if the data stream is the default data stream.
        """
        return not bool(self._name)
