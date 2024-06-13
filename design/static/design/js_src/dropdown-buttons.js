// Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch
// According to the copyright terms specified in the file "COPYRIGHT.md".
// SPDX-License-Identifier: GPL-3.0-or-later

// Add functions to handle dropdown buttons.
//
// Dropdown buttons are `button` elements that have a `data-dropdown-trigger` attribute which stores
// the id of the dropdown menu to be displayed.
//
export function activateDropdownButtonTriggers() {
    const $dropdownButtons = document.querySelectorAll('[data-dropdown-trigger]');
    $dropdownButtons.forEach(($dropdownButton) => {
        $dropdownButton.addEventListener('click', (event) => {
            event.preventDefault();
            if ($dropdownButton.disabled) {
                return; // Ignore this click if the button is disabled.
            }
            const $dropDown = $dropdownButton.closest('.dropdown');
            $dropDown.classList.toggle('is-active');
        });
    });
}

