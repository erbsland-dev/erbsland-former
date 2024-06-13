// Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch
// According to the copyright terms specified in the file "COPYRIGHT.md".
// SPDX-License-Identifier: GPL-3.0-or-later

import './global.js';
import {activateDropdownButtonTriggers} from "./dropdown-buttons";
import {activateActionButtonTriggers} from "./action-buttons";
import {activateModalOverlayTriggers} from "./modal-overlay";
import {activateTabTriggers} from "./tabs";
import {BrowserHelper, BrowserDocument} from "./browser";

// Make sure these will not get optimized away.
export {
    BrowserHelper,
    BrowserDocument,
    activateDropdownButtonTriggers,
    activateActionButtonTriggers,
    activateModalOverlayTriggers,
    activateTabTriggers,
};

