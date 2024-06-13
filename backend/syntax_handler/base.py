#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from typing import Callable, Iterator

from backend.splitter.analysis_window import AnalysisWindow
from backend.splitter.context_info import NodeContextInfo
from backend.splitter.line_reader import LineReader
from backend.splitter.split_level import SplitLevel
from backend.splitter.split_location import SplitLocation
from backend.splitter.text_fragment_node import TextFragmentNode
from backend.tools.extension import Extension


class SyntaxHandlerBase(Extension):
    """
    The base class for all document syntax instances.

    To implement a file syntax, create a subclass of this base class and overwrite these elements:

    - Overwrite the class attributes `name`, `verbose_name`.
    - Overwrite either `accepted_suffixes` or overwrite the class method `matches_syntax`.

    Now you can either implement the analysis of the file format by overwriting the `analyze_line()` method for a
    simple line-based format, or `split_file_into_fragments()` if your format is complex and not line based.

    Have a look at the example implementations and API documentation for details.
    """

    accepted_suffixes = []
    """A list of accepted suffixes for the implemented file format."""

    markdown_block_identifier: str = ""
    """An identifier that can be put after markdown code blocks to describe this syntax."""

    @classmethod
    def matches_syntax(cls, working_path: Path, original_path: Path) -> bool:
        """
        Test if this file has this syntax.

        The default implementation only checks the accepted suffixes and does not further check the file contents.
        Overwrite this method to implement your own matching algorithm.
        Use the path to the working file if you like to inspect its contents.

        :param working_path: The path to the file contents locally stored for import.
        :param original_path: The original path from the upload.
        """
        suffix = original_path.suffix[1:]
        return suffix in cls.accepted_suffixes

    def analyze_line(self, analysis_window: AnalysisWindow) -> SplitLevel:
        """
        Analyse an area in a text file.

        The lines do not contain the newline characters, therefore, empty lines are empty strings.

        **Returning a Split Level**

        This method must analyse a block of lines to detect split points. The method must return a split-level of
        the split point **above** the current line. If you use this default implementation, **do not** use the
        levels `SENTENCE` and `WORD` and use `LINE` for the smallest unit.

        Only use the split levels that are supported by the syntax you are using. It does not matter at which
        split-level you start and if you omit levels.

        **Setting the Split Level**

        The method is also allowed to alter the `split_level` property of the `Line` instances in the `analysis_window`.
        If a "next"-line has a split-level assigned, it is skipped without calling this method. You can also
        modify the `split_level` of previous lines. Any modifications inside the analysis window are allowed.

        The only exception is the `current` line. It will always be overwritten with the result of this
        function. So, while you can change it, it has no effect.

        :param analysis_window: The analysis window.
        :return: A split-level from `SplitLevel`.
        """
        return SplitLevel.LINE

    def parse_document_line_by_line(
        self,
        line_reader: LineReader,
        analyze_line: Callable[[AnalysisWindow], SplitLevel],
        window_size: int = 20,
    ) -> Iterator[SplitLocation]:
        """
        Parses a document line by line.

        For each line, that has no split-level assigned, the method `analyze_line` is called. This
        method must return the split-level for the given line. See `analyze_line()` for details how
        to implement this method.

        :param line_reader: The line reader to use.
        :param analyze_line: A function to analyze a window of lines of the file.
        :param window_size: The number of lines before and after the current line to pass to the analysis method.
        :return: A list with file positions and split levels.
        """
        analysis_window = line_reader.create_initial_window(window_size)
        while not analysis_window.is_at_end():
            if not analysis_window.current.split_level:
                analysis_window.current.split_level = analyze_line(analysis_window)
            if line := analysis_window.push_line(line_reader.read_line()):
                split_location = SplitLocation(
                    location=line.location,
                    line_number=line.line_number,
                    split_level=line.split_level,
                )
                if not line.meta.is_empty():
                    split_location.context = line.meta
                yield split_location
        for line in analysis_window.pop_remaining_lines():
            split_location = SplitLocation(
                location=line.location,
                line_number=line.line_number,
                split_level=line.split_level,
            )
            if not line.meta.is_empty():
                split_location.context = line.meta
            yield split_location

    def optimize_split_locations(self, split_locations: list[SplitLocation]):
        """
        Overwrite this method to optimize split locations based on the result of the `parse_file_line_by_line` method.

        Does nothing by default.

        :param split_locations: The split locations.
        """
        pass

    def split_document_into_fragments(self, line_reader: LineReader) -> TextFragmentNode:
        """
        Generate a tree of text fragments based on split locations in the file.

        The method reads through the file at `path`, analyzing it line by line to determine possible split locations.
        It then constructs a tree, where each node represents a text fragment, and nested nodes represent subfragments.

        Algorithm steps:
        1. Run `parse_file_line_by_line` to get all the possible split locations with their levels.
        2. Create initial fragments based on maximum split-level.
        3. Iterate through the split locations to divide the fragments further.
        4. Finally, set the end of each fragment to the file's total size.

        ```
                             [0, 1000]     <-- Root fragment spanning the entire file
                             |       |
                      [0, 500]       [500, 1000]  <-- Level 1 splits
                     |      |          |      |
               [0, 200]  [200, 500] [500, 700] [700, 1000]  <-- Level 2 splits
              |     |
        [0, 100] [100, 200]  <-- Level 3 splits
        ```

        :param line_reader: The line reader to use.
        :return: The root text fragment node.
        """
        # Get a list with all split locations in the file.
        split_locations = list(self.parse_document_line_by_line(line_reader, self.analyze_line))
        self.optimize_split_locations(split_locations)
        # Get a map with all levels returned by the syntax handler.
        split_level_map = dict(
            [
                (level, index + 1)
                for index, level in enumerate(sorted(set([loc.split_level for loc in split_locations])))
            ]
        )
        # Convert the split levels into indexes
        for split_location in split_locations:
            split_location.split_index = split_level_map[split_location.split_level]
        # The number of structure levels. Adding one for the root node.
        structure_levels = len(split_level_map) + 1
        root_fragment = TextFragmentNode.create_nodes(levels=structure_levels, begin=0, line_number=1)
        root_fragment.context = NodeContextInfo()  # The root node requires an empty context.
        for split_location in split_locations[1:]:
            root_fragment.split_at_level(split_location, structure_levels)
        root_fragment.set_end(line_reader.document_size)
        # Handle special cases:
        # 1. If the first split (at line 0) contains context information, add it to the first non_root block.
        if split_locations:
            first_split = split_locations[0]
            if first_split.context and not first_split.context.is_empty() and root_fragment.sub_fragments:
                first_fragment = root_fragment.sub_fragments[0]
                if not first_fragment.context:
                    first_fragment.context = NodeContextInfo()
                first_fragment.context.merge_location_context(first_split.split_level, first_split.context)
        # 2. Each node needs to be aware of a full context, up to the root node.
        #    Build a complete context for each node in the most memory efficient way possible.
        #    Use the fact, that each node that changes the context already contains a new context instance.
        root_fragment.push_context_to_sub_fragments()
        return root_fragment
