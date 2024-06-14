// Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch
// According to the copyright terms specified in the file "COPYRIGHT.md".
// SPDX-License-Identifier: GPL-3.0-or-later


export function activateTabTriggers() {
    const $tabTriggers = document.querySelectorAll('a[data-tab-page]');
    $tabTriggers.forEach(($tabTrigger) => {
        $tabTrigger.addEventListener('click', (event) => {
            const $ul = $tabTrigger.closest('ul');
            $ul.querySelectorAll('li').forEach(($li) => {
                $li.classList.remove('is-active');
            });
            $tabTrigger.closest('li').classList.add('is-active');
            const $selectedPage = document.getElementById($tabTrigger.dataset.tabPage);
            $selectedPage.closest('.tabs-content').querySelectorAll('.tabs-page').forEach(($page) => {
                $page.classList.remove('is-active');
            });
            $selectedPage.classList.add('is-active');
            // If there is a hidden input in the "tabs" container, store the selected page to be submitted on POST.
            const $selectedPageForForm = $tabTrigger.closest('.tabs').querySelector('input[type="hidden"]');
            if ($selectedPageForForm) {
                $selectedPageForForm.value = $tabTrigger.dataset.tabPage;
            }
        });
    });
}

