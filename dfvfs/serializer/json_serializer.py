"""The JSON serializer object implementation."""

import json

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.path import path_spec
from dfvfs.serializer import serializer


class _PathSpecJsonDecoder(json.JSONDecoder):
    """Path specification JSON decoder."""

    _CLASS_TYPES = frozenset(["PathSpec"])

    _BYTES_CLASS_TYPE = "bytes"

    def __init__(self, *args, **kargs):
        """Initializes a path specification JSON decoder."""
        super().__init__(*args, object_hook=self._ConvertDictToObject, **kargs)

    def _ConvertDictToObject(self, json_dict):
        """Converts a JSON dict into a path specification object.

        The dictionary of the JSON serialized objects consists of:
        {
            '__type__': 'PathSpec'
            'type_indicator': 'OS'
            'parent': { ... }
            ...
        }

        Here '__type__' indicates the object base type in this case this should
        be 'PathSpec'. The rest of the elements of the dictionary make up the
        path specification object properties. Note that json_dict is a dict of
        dicts and the _ConvertDictToObject method will be called for every dict.
        That is how the path specification parent objects are created.

        Args:
          json_dict (dict[str, object]): JSON serialized objects.

        Returns:
          PathSpec: a path specification.

        Raises:
          TypeError: if the JSON serialized object does not contain a '__type__'
              attribute that contains 'PathSpec' or 'bytes'.
        """
        # Use __type__ to indicate the object class type.
        class_type = json_dict.get("__type__")

        # Convert a JSON serialized bytes object back into bytes. Note that
        # the object hook is called bottom-up, so bytes values are restored
        # before the path specification object that contains them.
        if class_type == self._BYTES_CLASS_TYPE:
            return bytes.fromhex(json_dict["hex"])

        if class_type not in self._CLASS_TYPES:
            raise TypeError("Missing path specification object type.")

        # Remove the class type from the JSON dict since we cannot pass it.
        del json_dict["__type__"]

        type_indicator = json_dict.get("type_indicator")
        if type_indicator:
            del json_dict["type_indicator"]

        # Convert row_condition back to a tuple.
        if "row_condition" in json_dict:
            json_dict["row_condition"] = tuple(json_dict["row_condition"])

        path_spec_object = path_spec_factory.Factory.NewPathSpec(
            type_indicator, **json_dict
        )

        if type_indicator == definitions.TYPE_INDICATOR_OS:
            # OSPathSpec() will change the location to an absolute path
            # here we want to preserve the original location.
            path_spec_object.location = json_dict.get("location")

        return path_spec_object


class _PathSpecJsonEncoder(json.JSONEncoder):
    """Path specification object JSON encoder."""

    # Note: that the following functions do not follow the style guide
    # because they are part of the json.JSONEncoder object interface.
    # pylint: disable=invalid-name,method-hidden

    def default(self, path_spec_object):  # pylint: disable=arguments-renamed
        """Converts a path specification object into a JSON dictionary.

        The resulting dictionary of the JSON serialized objects consists of:
        {
            '__type__': 'PathSpec'
            'type_indicator': 'OS'
            'parent': { ... }
            ...
        }

        Here '__type__' indicates the object base type in this case this should
        be 'PathSpec'. The rest of the elements of the dictionary make up the
        path specification object properties. The properties are copied from
        the path specification object attributes, so that every attribute that
        defines the identity of the path specification (its comparable
        representation) is preserved. Note that this method is called
        recursively for every path specification object and creates a dict of
        dicts in the process that is transformed into a JSON string by the
        JSON encoder.

        Args:
          path_spec_object (PathSpec): a path specification.

        Returns:
          dict[str, object]: JSON serialized objects.

        Raises:
          TypeError: if not an instance of PathSpec.
        """
        if not isinstance(path_spec_object, path_spec.PathSpec):
            raise TypeError

        json_dict = {"__type__": "PathSpec"}
        for property_name, property_value in path_spec_object.__dict__.items():
            if property_value is None:
                continue

            if property_name == "parent":
                property_value = self.default(property_value)
            elif isinstance(property_value, bytes):
                # JSON does not support bytes so they are stored as a
                # hexadecimal string with a type indicator.
                property_value = {
                    "__type__": "bytes",
                    "hex": property_value.hex(),
                }
            elif isinstance(property_value, tuple):
                # Convert tuples such as row_condition to a list.
                property_value = list(property_value)

            json_dict[property_name] = property_value

        json_dict["type_indicator"] = path_spec_object.type_indicator

        return json_dict


class JsonPathSpecSerializer(serializer.PathSpecSerializer):
    """JSON path specification serializer object."""

    @classmethod
    def ReadSerialized(
        cls, json_string
    ):  # pylint: disable=arguments-differ,arguments-renamed
        """Reads a path specification from serialized form.

        Args:
          json_string (str): JSON serialized path specification.

        Returns:
          PathSpec: a path specification.
        """
        json_decoder = _PathSpecJsonDecoder()
        return json_decoder.decode(json_string)

    @classmethod
    def WriteSerialized(
        cls, path_spec_object
    ):  # pylint: disable=arguments-differ,arguments-renamed
        """Writes a path specification to serialized form.

        Args:
          path_spec_object (PathSpec): a path specification.

        Returns:
          str: JSON serialized path specification.
        """
        return json.dumps(path_spec_object, cls=_PathSpecJsonEncoder)
