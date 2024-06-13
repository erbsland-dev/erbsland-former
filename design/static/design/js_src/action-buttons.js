// Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch
// According to the copyright terms specified in the file "COPYRIGHT.md".
// SPDX-License-Identifier: GPL-3.0-or-later

// Add functions to handle action buttons and action selections.
//
// Action buttons are `<button>` or `<a>` elements that use the `<form>` they are defined in to submit it's
// action to the application. With the attribute `--data-action-event="change"`, `<select>` tags are supported
// as well.
//
// The tag `{% action_button_trigger '<action name>' '<optional action value>' %}` inside any clickable HTML
// converts it into an action button. When clicked, the original event is suppressed. Hidden inputs with
// the names `action` and `action_value` are added to the surrounding form and then the form is submitted.
//
// The tag `{% action_select_trigger '<action name>' '<optional field value>' %}` trigger a form submission as soon
// the selection has been changed.
//
export function activateActionButtonTriggers() {
    const $actionElements = document.querySelectorAll('[data-action-trigger]');
    $actionElements.forEach(($actionElement) => {
        const eventName = $actionElement.dataset.actionEvent || 'click';
        $actionElement.addEventListener(eventName, (event) => {
            const isDisabled = $actionElement.getAttribute('disabled') !== null;
            const isSelected = $actionElement.classList.contains('is-selected');
            if (isDisabled || isSelected) {
                return; // Ignore this click if the button is disabled.
            }
            const isSelectElement = ($actionElement.tagName.toLowerCase() === 'select');
            if (!isSelectElement) {
                event.preventDefault(); // Ignore the default behaviour, unless this is a <select> element.
            }
            const actionName = $actionElement.dataset.actionTrigger;
            let actionValue = ''
            if (isSelectElement) {
                actionValue = $actionElement.value;
            } else {
                actionValue = $actionElement.dataset.actionValue;
            }
            const restoreScrollPos = $actionElement.dataset.restoreScrollPos || 0;
            if (restoreScrollPos) {
                localStorage.setItem('scrollPosition', window.scrollY.toString());
            }
            const $form = $actionElement.closest('form');
            const formUrl = $actionElement.dataset.actionFormUrl || '';
            if (formUrl) {
                $form.action = formUrl
            }
            let $inputActionName = $form.querySelector('input[name="action"]');
            let $inputActionValue = $form.querySelector('input[name="action_value"]');
            // If the hidden inputs for action and action_value don't exist, create them
            if (!$inputActionName) {
               $inputActionName = document.createElement('input');
               $inputActionName.type = 'hidden';
               $inputActionName.name = 'action';
               $form.appendChild($inputActionName);
            }
            if (!$inputActionValue) {
               $inputActionValue = document.createElement('input');
               $inputActionValue.type = 'hidden';
               $inputActionValue.name = 'action_value';
               $form.appendChild($inputActionValue);
            }
            // Set the action and action_value
            $inputActionName.value = actionName;
            $inputActionValue.value = actionValue;
            // Now submit the form with the new values.
            // Use an event, to allow other code update fields in the form before its submitted.
            $form.dispatchEvent(new Event('submit', { 'bubbles': true, 'cancelable': true }));
            $form.submit();
        });
    });

    // Restore a scroll position that was saved with the action button.
    window.addEventListener('load', () => {
        const savedScrollPosition = localStorage.getItem('scrollPosition');
        if (savedScrollPosition !== null) {
            window.scrollTo(0, parseInt(savedScrollPosition));
            localStorage.removeItem('scrollPosition');
        }
    });
}

