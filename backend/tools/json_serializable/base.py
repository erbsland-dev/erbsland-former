#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional, Any, Self

from backend.tools.json_serializable.meta import JsonSerializableMeta
from backend.tools.json_serializable.names import TYPE_FIELD_NAME, VERSION_FIELD_NAME

JsonTypes = dict[str, Any] | list[Any] | str | int | float | bool


class JsonSerializable(metaclass=JsonSerializableMeta):
    """
    Base class for very simple JSON serializable objects.

    By default, this class tries to serialize all attributes except ones that start with an underline.
    This behaviour can be changed by setting the `serialized_attributes` list, with all attribute names that
    shall be serialized.

    The constructor of the subclass must set all attributes to default values that have the expected type which
    should be deserialized from JSON data. By default, the deserialized type from JSON is compared with the
    type of the attribute.

    If you like to serialize custom types, you *must* list them in the `serialized_classes` attribute.
    """

    serialized_name = None
    serialized_version = 1
    serialized_attributes: Optional[list[str]] = None
    serialized_classes: Optional[list[type["JsonSerializable"]]] = None

    @classmethod
    def get_serialized_name(cls) -> str:
        if cls.serialized_name is None:
            return cls.__name__
        return cls.serialized_name

    @classmethod
    def get_serialized_version(cls) -> int:
        return cls.serialized_version

    @classmethod
    def get_serialized_attributes(cls) -> Optional[list[str]]:
        return cls.serialized_attributes

    @classmethod
    def get_serialized_classes(cls) -> Optional[list[type["JsonSerializable"]]]:
        return cls.serialized_classes or []

    @classmethod
    def get_serializable_type(cls, serialized_name: str) -> type["JsonSerializable"]:
        serialized_classes = cls.get_serialized_classes()
        if not serialized_classes:
            ValueError(f"Could not find serializable type for name '{serialized_name}'. No valid types specified.")
        for serialized_class in serialized_classes:
            if serialized_class.serialized_name == serialized_name:
                return serialized_class
        raise ValueError(f"Could not find serializable type for name '{serialized_name}'. Type not in list.")

    @staticmethod
    def _is_json_serializable_type(obj) -> bool:
        return obj is None or isinstance(obj, (str, int, float, bool))

    @staticmethod
    def _to_json(obj) -> JsonTypes:
        if JsonSerializable._is_json_serializable_type(obj):
            return obj
        elif isinstance(obj, list):
            return list(JsonSerializable._to_json(o) for o in obj)
        elif isinstance(obj, dict):
            return dict((str(k), JsonSerializable._to_json(o)) for k, o in obj.items())
        elif isinstance(obj, JsonSerializable):
            return obj.to_json()
        raise TypeError(f"The type {obj.__class__} is not supported by 'JsonSerializable'.")

    @staticmethod
    def _shall_serialize(key: str, value: Any, valid_keys: list[str] = None) -> bool:
        if key.startswith("_"):
            return False
        if value is None or callable(value):
            return False
        if valid_keys is not None:
            if key not in valid_keys:
                return False
        return True

    def to_json(self, *, add_type=True, add_version=True) -> JsonTypes:
        """
        Converts the attributes of this class into a JSON serializable dictionary.

        By default, all attributes that aren't callable and do not start with an underscore are serialized. The
        attributes must either a `str`, `int`, `float` or `bool` or a `list` or `dict` with a `str` as key and
        one of the supported types. If the attribute is not of that type, it must be an instance that is derived
        from `JsonSerializable`.

        :param add_type: If the field `_type` shall be added to the dictionary.
        :param add_version: If the field `_version` shall be added to the dictionary.
        :return: A JSON serializable dict.
        """
        valid_keys = self.get_serialized_attributes()
        result = dict(
            [
                (key, self._to_json(value))
                for key, value in self.__dict__.items()
                if self._shall_serialize(key, value, valid_keys)
            ]
        )
        if add_type:
            result[TYPE_FIELD_NAME] = self.get_serialized_name()
        if add_version:
            result[VERSION_FIELD_NAME] = self.get_serialized_version()
        return result

    @classmethod
    def _guess_from_json(cls, json_value: Any) -> Any:
        """
        Converts a value from a JSON document into a Python object by guessing its correct target type
        based on the provided structure.

        :param json_value: The JSON value.
        :return: The converted value.
        """
        if isinstance(json_value, str | int | float | bool):
            return json_value
        if isinstance(json_value, dict):
            if TYPE_FIELD_NAME in json_value:
                new_type = cls.get_serializable_type(json_value[TYPE_FIELD_NAME])
                return new_type.from_json(json_value)
            return [(key, cls._guess_from_json(value)) for key, value in json_value.items()]
        if isinstance(json_value, list):
            return [cls._guess_from_json(value) for value in json_value]
        raise TypeError("Unexpected type in JSON document.")

    @classmethod
    def _from_json(cls, *, json_value: Any, local_value: Any) -> Any:
        """
        Converts a value from the JSON dictionary into the correct value to assign to the new object.

        :param json_value: The value from the JSON dictionary.
        :param local_value: The current default value from the new object.
        :return: The new value that shall be assigned to the new object.
        """
        new_value = cls._guess_from_json(json_value)
        if isinstance(local_value, JsonSerializable):
            if not isinstance(new_value, JsonSerializable):
                raise ValueError("Expected a JsonSerializable, but something else.")
            if new_value.get_serialized_name() != local_value.get_serialized_name():
                raise ValueError(
                    f"Expected a '{local_value.get_serialized_name()}' type, but got '{new_value.get_serialized_name()}'."
                )
        elif not isinstance(new_value, type(local_value)):
            raise ValueError(f"Expected a '{type(local_value)}' type, but got '{type(new_value)}")
        return new_value

    @classmethod
    def from_json(cls, json_dict: dict[str, Any], *, version: int = None, verify_type=True) -> Self:
        """
        Create a new object from the JSON dictionary.

        By default, this method follows the same rules as the serialization rules. It tests of the JSON dictionary
        contains one of the attributes defined in the object and tests if the type matches.

        :param json_dict: The dictionary to be used to create the new instance.
        :param version: Optional version of the JSON data, to be used instead of `_version` in the dictionary.
        :param verify_type: If `True`, a `_type` field is expected in the dictionary and verified.
        :return:
        """
        if version is None:
            if VERSION_FIELD_NAME not in json_dict:
                raise ValueError(f"Missing '{VERSION_FIELD_NAME}' in serialized JSON.")
            version = json_dict[VERSION_FIELD_NAME]
            if not isinstance(version, int):
                raise ValueError(f"'{VERSION_FIELD_NAME}' must be an integer.")
            if TYPE_FIELD_NAME not in json_dict:
                raise ValueError(f"Missing '{TYPE_FIELD_NAME}' in serialized JSON.")
        if version > cls.get_serialized_version():
            raise ValueError(
                f"The serialized data version {version} is larger than "
                f"the version of his class {cls.get_serialized_version()}"
            )
        if verify_type:
            if TYPE_FIELD_NAME not in json_dict:
                raise ValueError(f"Missing '{TYPE_FIELD_NAME}' in dictionary.")
            type_name = json_dict[TYPE_FIELD_NAME]
            if not isinstance(type_name, str):
                raise ValueError(f"'{TYPE_FIELD_NAME}' must be a string.")
            if type_name != cls.get_serialized_name():
                raise ValueError(f"'{TYPE_FIELD_NAME}' does not match the type name of this class.")
        valid_keys = cls.get_serialized_attributes()
        new_obj = cls()
        for key, json_value in json_dict.items():
            if not hasattr(new_obj, key):
                continue  # Ignore any values that are not defined in the new object.
            local_value = getattr(new_obj, key)
            if not cls._shall_serialize(key, local_value, valid_keys):
                continue  # Ignore values that wouldn't be serialized.
            setattr(new_obj, key, cls._from_json(json_value=json_value, local_value=local_value))
        return new_obj
