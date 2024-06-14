// Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch
// According to the copyright terms specified in the file "COPYRIGHT.md".
// SPDX-License-Identifier: GPL-3.0-or-later


// Add functions for modal overlays.
export function activateModalOverlayTriggers() {

    // Function to open a modal.
    function openModal($el) {
        $el.classList.add('is-active');
        const $focusElement = $el.querySelector('.has-select-all-on-show');
        if ($focusElement) {
            // Check if the element is focusable and has the select method.
            if (typeof $focusElement.select === "function") {
                $focusElement.select();
            }
        }
    }

    // Function to close a modal.
    function closeModal($el) {
        $el.classList.remove('is-active');
    }

    // Function to close all modals.
    function closeAllModals() {
        const $modalElements = document.querySelectorAll('.modal');
        $modalElements.forEach(($modal) => {
            closeModal($modal);
        });
    }

    // Add a click event on buttons to open a specific modal.
    document.querySelectorAll('[data-modal-trigger]').forEach(($trigger) => {
        const modalId = $trigger.dataset.modalTrigger;
        const $target = document.getElementById(modalId);
        $trigger.addEventListener('click', (event) => {
            event.preventDefault();
            openModal($target);
        });
    });

    // Add a click event on various child elements to close the parent modal.
    const $modalCloseElements = document.querySelectorAll('.modal-background, .modal-close, .modal-card-head .delete, .modal-close-button');
    $modalCloseElements.forEach(($close) => {
        const $target = $close.closest('.modal');
        $close.addEventListener('click', (event) => {
            event.preventDefault();
            closeModal($target);
        });
    });

    // Add a keyboard event to close all modals.
    document.addEventListener('keydown', (event) => {
        if (event.code === 'Escape') {
            closeAllModals();
        }
    });
}

