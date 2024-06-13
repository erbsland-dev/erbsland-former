#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import enum


class StatisticHighlight(enum.StrEnum):
    NONE = "none"
    GOOD = "good"
    BAD = "bad"
