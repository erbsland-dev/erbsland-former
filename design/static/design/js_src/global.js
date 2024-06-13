// Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch
// According to the copyright terms specified in the file "COPYRIGHT.md".
// SPDX-License-Identifier: GPL-3.0-or-later

document.addEventListener('DOMContentLoaded', () => {

    // Add the trigger for the collapsed menu bar.
    const $navBarBurgers = document.querySelectorAll('.navbar-burger');
    $navBarBurgers.forEach($navBarBurger => {
        $navBarBurger.addEventListener('click', () => {
            const targetId = $navBarBurger.dataset.target;
            const $target = document.getElementById(targetId);
            $navBarBurger.classList.toggle('is-active');
            $target.classList.toggle('is-active');
        });
    });

    // Add an event that notification boxes can be closed using the "delete" button.
    const $deleteButtons = document.querySelectorAll('.notification .delete');
    $deleteButtons.forEach(($deleteButton) => {
        const $notification = $deleteButton.parentNode;
        $deleteButton.addEventListener('click', () => {
            $notification.parentNode.removeChild($notification);
        });
    });

});
