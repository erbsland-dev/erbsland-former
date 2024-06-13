#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from abc import ABCMeta


class JsonSerializableMeta(ABCMeta):
    """
    The metaclass for JSON serializable objects.

    Makes sure subclass define the class attribute `serialized_name` and `serialized_version`.
    If a subclass ends in `Base`, these checks are ignored.
    """

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        if cls.__name__ == "JsonSerializable" or not cls.__name__.endswith("Base"):
            return cls
        if hasattr(cls, "serialized_name"):
            serialized_name = getattr(cls, "serialized_name")
            if serialized_name is not None:
                if not isinstance(serialized_name, str) or not serialized_name.strip():
                    raise TypeError(f"{cls.__name__} must have a non-empty 'serialized_name' class variable.")
        serialized_version = getattr(cls, "serialized_version")
        if not isinstance(serialized_version, int) or serialized_version < 1:
            raise TypeError(f"{cls.__name__} must have a 'serialized_version' class variable with a positive integer.")
        if hasattr(cls, "serialized_attributes"):
            serialized_attributes = getattr(cls, "serialized_attributes")
            if serialized_attributes is not None:
                if not isinstance(serialized_attributes, list):
                    raise TypeError(f"{cls.__name__}.serialized_attributes must be a list.")
                if not serialized_attributes:
                    raise TypeError(f"{cls.__name__}.serialized_attributes must not be empty.")
                for entry in serialized_attributes:
                    if not isinstance(entry, str):
                        raise TypeError(f"{cls.__name__}.serialized_attributes must only contain strings.")
        return cls
