#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import enum
from functools import cached_property, lru_cache
from typing import Optional, Iterator, Tuple

from backend.enums.review_state import ReviewStateCounts
from backend.enums.transformation_state import TransformationStateCounts
from backend.models.document import Document
from backend.models.revision import Revision
from backend.syntax_handler import syntax_manager


class DocumentTreeNodeType(enum.StrEnum):
    """
    Type of file system node.
    """

    DOCUMENT = "document"
    FOLDER = "folder"


class DocumentTreeNode:
    def __init__(self, *, document: Document = None, folder_path: str = None, with_document_details: bool = False):
        """
        Create a new document node.

        :param document: The document node from the db, is specified a document node is created.
        :param with_document_details: If document details, like review states and the fragment count
            shall be included. This requires to accessing the document object for every node.
        """
        self.parent: Optional["DocumentTreeNode"] = None
        self.children: list["DocumentTreeNode"] = []
        self.index: int = -1  # Index of flattened tree to alternate row colours properly.
        self.review_states: Optional[ReviewStateCounts] = None
        if document is None:
            if folder_path is None:
                raise ValueError("The folder_path must be specified for folder nodes.")
            self.document_id = None
            self.path = folder_path
            return
        if folder_path:
            raise ValueError("Folder path must not be specified for document nodes.")
        self.document_id: int = document.pk
        self.path: str = document.path
        if with_document_details:
            self.fragment_count: int = document.fragment_count
            self.review_states = document.review_states()
            self.transformation_states = document.transformation_states()
            self.document_syntax = syntax_manager.verbose_name(document.document_syntax)

    @cached_property
    def path_parts(self) -> list[str]:
        return self.path.strip("/").split("/")

    @cached_property
    def level(self) -> int:
        return self.path.count("/")

    @cached_property
    def type(self) -> DocumentTreeNodeType:
        if self.document_id is not None:
            return DocumentTreeNodeType.DOCUMENT
        return DocumentTreeNodeType.FOLDER

    @cached_property
    def name(self) -> str:
        if self.is_root:
            return "/"
        return self.path_parts[-1]

    @cached_property
    def folder(self) -> str:
        if self.is_root:
            return ""
        return "/".join(self.path_parts[:-1])

    @cached_property
    def suffix(self) -> str:
        if self.type == DocumentTreeNodeType.DOCUMENT and "." in self.name.lstrip("."):
            return self.name.split(".")[-1]
        return ""

    @cached_property
    def is_root(self) -> bool:
        return self.path == ""

    def flatten(self) -> Iterator["DocumentTreeNode"]:
        yield self
        for child in self.children:
            yield from child.flatten()

    def summarize_meta_data(self):
        if self.children and not self.review_states:
            review_states = ReviewStateCounts(initialize_with_zero=True)
            transformation_states = TransformationStateCounts(initialize_with_zero=True)
            for child in self.children:
                child.summarize_meta_data()
                if child.review_states:
                    review_states.add_other(child.review_states)
                if child.transformation_states:
                    transformation_states.add_other(child.transformation_states)
            self.review_states = review_states
            self.transformation_states = transformation_states


class DocumentTree:
    def __init__(self, revision: Revision, with_document_details=False):
        """
        Create a document tree for the given revision.

        :param revision: The revision to create the document tree from.
        :param with_document_details: If document details, like review states and the fragment count
            shall be included. This will access every document in the tree and summarizes the states for
            the parents and the whole tree.
        """
        self._root_node: DocumentTreeNode  # The root node.
        self._node_list: list[DocumentTreeNode]  # A flat list with all nodes in alphabetical order.
        self._document_list: list[DocumentTreeNode] = []  # A flat list with all documents.
        self._with_review_states = with_document_details
        self._create_node_tree_for_revision(revision)

    @property
    def root_node(self) -> DocumentTreeNode:
        return self._root_node

    @property
    def node_list(self) -> list[DocumentTreeNode]:
        return self._node_list

    @property
    def document_count(self) -> int:
        return len(self._document_list)

    @property
    def has_documents(self) -> bool:
        """Test if there are documents in this tree."""
        return self.document_count > 0

    @property
    def has_no_documents(self) -> bool:
        """Negation so simplify template code. Test if there are no documents in this tree."""
        return self.document_count == 0

    @lru_cache
    def _get_index_and_document(self, document_id: int) -> Tuple[int, DocumentTreeNode]:
        for index, node in enumerate(self._document_list):
            if node.document_id == document_id:
                return index, node
        raise ValueError("Unknown document_id")

    def has_next_document(self, document_id: int):
        index, node = self._get_index_and_document(document_id)
        return index < (len(self._document_list) - 1)

    def has_previous_document(self, document_id: int) -> bool:
        index, node = self._get_index_and_document(document_id)
        return index > 0

    def get_next_document_id(self, document_id: int) -> int:
        index, node = self._get_index_and_document(document_id)
        if index < (len(self._document_list) - 1):
            return self._document_list[index + 1].document_id
        return -1

    def get_previous_document_id(self, document_id: int) -> int:
        index, node = self._get_index_and_document(document_id)
        if index > 0:
            return self._document_list[index - 1].document_id
        return -1

    def get_first_document_id_with_fractions_in_review_pending_state(self) -> Optional[int]:
        """
        Get the first document id of a document that has fractions in review pending state.

        :return: The id or None of no document has such fractions.
        """
        for node in self._document_list:
            if node.type == DocumentTreeNodeType.DOCUMENT and node.review_states.has_pending_reviews:
                return node.document_id
        return None

    def _create_node_tree_for_revision(self, revision: Revision) -> None:
        self._root_node = DocumentTreeNode(folder_path="")
        node_map: dict[str, DocumentTreeNode] = {"": self._root_node}
        # Create all documents and it's subdirectories.
        for document in revision.documents.exclude(is_preview=True).all():
            browser_node = DocumentTreeNode(document=document, with_document_details=self._with_review_states)
            node_map[browser_node.path] = browser_node
            if browser_node.level > 0:
                for i in range(browser_node.level):
                    path = "/".join(browser_node.path_parts[: i + 1])
                    if path not in node_map:
                        node_map[path] = DocumentTreeNode(folder_path=path)
        # Link the nodes into a tree structure
        for browser_node in node_map.values():
            if browser_node.is_root:
                continue
            parent_node = node_map[browser_node.folder]
            browser_node.parent = parent_node
            parent_node.children.append(browser_node)
        # Sort the nodes alphabetically
        for browser_node in node_map.values():
            browser_node.children.sort(key=lambda x: (x.type, x.name.lower()))
        # Update the index and document list
        self._node_list = list(self._root_node.flatten())
        for index, node in enumerate(self._node_list):
            node.index = index
            if node.type == DocumentTreeNodeType.DOCUMENT:
                self._document_list.append(node)
        if self._with_review_states:
            self._root_node.summarize_meta_data()
