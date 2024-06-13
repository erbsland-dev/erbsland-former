#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional, Iterator, Self

from backend.splitter.split_location_context import SplitLocationContext
from backend.splitter.context_info import NodeContextInfo
from backend.splitter.split_location import SplitLocation


class TextFragmentNode:
    """
    A text fragment node.
    """

    def __init__(self, begin: int, line_number: Optional[int]):
        """
        Create a new text fragment node.

        :param begin: The beginning of the fragment in the file.
        """
        self._begin: int = begin
        """The beginning position in the file."""
        self._end: Optional[int] = None
        """The end position in the file."""
        self._sub_fragments: list[Self] = []
        """A list of subfragments."""
        self._line_number: Optional[int] = line_number
        """The first line number in this text fragment."""
        self.context: Optional[NodeContextInfo] = None
        """Context info for this node."""
        self.size: Optional[int] = None
        """The calculated size of this fragment - used by external tools as storage attribute."""

    @property
    def begin(self) -> int:
        """The beginning of this fragment, as location from the file."""
        return self._begin

    @property
    def end(self) -> int:
        """The end of this fragment, as location from the file."""
        return self._end

    @property
    def sub_fragments(self) -> list[Self]:
        """A list of subfragments."""
        return self._sub_fragments

    @property
    def line_number(self) -> Optional[int]:
        """The first line number of this fragment."""
        return self._line_number

    @classmethod
    def create_nodes(cls, levels: int, begin: int = 0, line_number: Optional[int] = None) -> Self:
        """
        Create an initial structure `fragment_levels` deep with open fragments, starting at position `begin`.

        :param levels: The number of fragment levels.
        :param begin: The beginning position for the fragments.
        :param line_number: The first line number for this node.
        :return: The root node for the structure.
        """
        fragments = [cls(begin=begin, line_number=line_number) for _ in range(levels)]
        for index in reversed(range(1, levels)):
            fragments[index - 1].add_node(fragments[index])
        return fragments[0]

    def split_at_level(self, split_location: SplitLocation, structure_levels: int) -> None:
        """
        Split the structure at `level` and `position`, creating all required nodes for the split.

        :param split_location: The location for the split. Must have `split_index` set.
        :param structure_levels: The number of levels for the whole structure.
        """
        if split_location.location < 0:
            raise ValueError("The `file_location` must not be negative.")
        if structure_levels < 2:
            raise ValueError("There must be more than one structure level.")
        if split_location.split_index <= 0:
            raise ValueError("`split_index` must not be zero or negative.")
        if split_location.split_index >= structure_levels:
            raise ValueError("You can not split at this level.")
        parent_node: Optional[Self] = None
        node = self
        for _ in range(split_location.split_index):
            if not node.sub_fragments:
                raise ValueError("There are no enough levels for the split.")
            parent_node = node
            node = node.sub_fragments[-1]
        node.set_end(split_location.location)
        levels_to_create = structure_levels - split_location.split_index
        node = self.create_nodes(
            levels=levels_to_create,
            begin=split_location.location,
            line_number=split_location.line_number,
        )
        if split_location.context and not split_location.context.is_empty():
            if not node.context:
                node.context = NodeContextInfo()
            node.context.merge_location_context(split_location.split_level, split_location.context)
        parent_node.add_node(node)

    def set_end(self, position: int) -> None:
        """
        Sets the end position for all open fragments.

        :param position: The end position.
        """
        node = self
        while node:
            node._end = position
            if node.sub_fragments:
                node = node.sub_fragments[-1]
            else:
                node = None

    def add_node(self, node: Self):
        """
        Add a subfragment

        :param node: The subfragment.
        """
        # The way how the algorithm works, any previous subfragment will never be touched again.
        # Therefore, we can run an optimization pass on it.
        if self._sub_fragments:
            self._sub_fragments[-1].fold()
        self._sub_fragments.append(node)

    def fold(self):
        """
        Remove subfragments that have no function.
        """
        # If there is only one subfragment, it is redundant and should be removed.
        while len(self._sub_fragments) == 1:
            node_to_remove = self._sub_fragments[0]
            # Make sure we don't lose any context information while folding the structure.
            if node_to_remove.context:
                for fragment in node_to_remove._sub_fragments:
                    if not fragment.context:
                        fragment.context = node_to_remove.context  # Reuse the existing one.
                    else:
                        fragment.context.merge_parent_context(node_to_remove.context)  # Merge
            self._sub_fragments = node_to_remove._sub_fragments
        for subfragment in self._sub_fragments:
            subfragment.fold()

    def push_context_to_sub_fragments(self):
        """
        Pushes the context of this node to its sub-fragments.
        """
        for subfragment in self._sub_fragments:
            if not subfragment.context:
                # In case the subfragment has no own context, no change is required and this context can be reused.
                subfragment.context = self.context
            else:
                # If a subfragment has already a context, just merge them.
                subfragment.context.merge_parent_context(self.context)
            # Recursively repeat for all sub-fragments.
            subfragment.push_context_to_sub_fragments()

    def flatten(self) -> Iterator[Self]:
        """
        Flatten the tree to do debugging and analysis.
        """
        yield self
        for subfragment in self._sub_fragments:
            yield from subfragment.flatten()

    @property
    def size_in_bytes(self):
        """
        Get the size of this fragment in bytes.
        """
        if not self._end:
            return None
        return self._end - self._begin

    def get_all_nodes(self) -> Iterator[Self]:
        """
        Generator to get a flat list with all nodes in root to leave order.
        """
        yield self
        if self._sub_fragments:
            for sub_fragment in self._sub_fragments:
                yield from sub_fragment.get_all_nodes()

    def _tree_str_list(self, level: int) -> list[str]:
        result: list[str] = [f'{"  " * level}[{self._begin} - {self._end}]']
        for subfragment in self._sub_fragments:
            result.extend(subfragment._tree_str_list(level + 1))
        return result

    def to_tree_str(self) -> str:
        return "\n".join(self._tree_str_list(0))

    def __str__(self):
        context = ", ".join(str(e) for e in self.context.entries)
        return f"begin: {self._begin}, end: {self._end}, sub fragments: {len(self._sub_fragments)}, context: {context}"
