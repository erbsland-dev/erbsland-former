#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from abc import ABC, abstractmethod
from typing import Optional, Any

from backend.transformer.fragment_access import FragmentAccess


class TransformerDocumentContext(ABC):
    """
    The context that is accessible by the transformer processor.
    """

    @property
    @abstractmethod
    def document_name(self) -> str:
        """Get the name of the document."""
        pass

    @property
    @abstractmethod
    def document_folder(self) -> str:
        """Get the folder of the document."""
        pass

    @property
    @abstractmethod
    def document_path(self) -> str:
        """Get the path of the document. This is the name and folder combined."""
        pass

    @property
    @abstractmethod
    def document_syntax(self) -> str:
        """Get the identifier of the document syntax."""
        pass

    def to_dict(self) -> dict[str, Any]:
        """Create all context values in a dictionary."""
        return {
            "document_name": self.document_name,
            "document_folder": self.document_folder,
            "document_path": self.document_path,
            "document_syntax": self.document_syntax,
        }


class TransformerFragmentContext(TransformerDocumentContext):
    """
    The context that is accessible by the transformer processor.
    """

    @property
    @abstractmethod
    def fragment_index(self) -> int:
        """Get the index of the fragment inside the current document."""
        pass

    @property
    @abstractmethod
    def fragment_count(self) -> int:
        """Get the number of fragments in the current document."""
        pass

    @property
    @abstractmethod
    def fragment_context(self) -> dict[str, str]:
        """Get the context information for this fragment."""
        pass

    @property
    @abstractmethod
    def processed_count(self) -> int:
        """Get the number of processed fragments that can be accessed via `get_processed`"""
        pass

    @abstractmethod
    def get_processed(self, steps_back: int = 0) -> Optional[FragmentAccess]:
        """
        Get one of the previously processed fragments.

        :param steps_back: How many fragments to step back. Zero means the immediately last processed fragment.
        :return: The fragment data or `None` of `steps_back` is out of the valid range.
        """
        pass

    @property
    @abstractmethod
    def previous_count(self) -> int:
        """The number of fragments in the current document before this fragment."""
        pass

    @abstractmethod
    def get_previous(self, steps_back: int = 0) -> Optional[FragmentAccess]:
        """
        Get one of the previous fragments in this document.

        :param steps_back: The number of steps back from the current fragment. Zero means the immediately previous
            fragment in the document.
        :return: The fragment data or `None` of `steps_back` is out of the valid range.
        """
        pass

    def to_dict(self) -> dict[str, Any]:
        """Create all context values in a dictionary."""
        return {
            **(super().to_dict()),
            "fragment_index": self.fragment_index,
            "fragment_count": self.fragment_count,
            "processed_count": self.processed_count,
            **self.fragment_context,
        }
