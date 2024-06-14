// Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch
// According to the copyright terms specified in the file "COPYRIGHT.md".
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * A single document for the browser.
 */
class BrowserDocument {

    /**
     * Create a new browser document.
     *
     * @param {int} index The index. 0 for the root document.
     * @param {string} name The name
     * @param {int} parentIndex The parent document identifier.
     * @param {bool} isDocument If this is a document (not a folder).
     */
    constructor(index, name, parentIndex, isDocument) {
        this.index = index;
        this.name = name;
        this.parentIndex = parentIndex;
        this.isDocument = isDocument;
        this.parent = null; // The parent node.
        this.children = []; // A list with all child nodes.
        this.checkbox = null; // The checkbox element.
        this.foldingHandle = null; // The folding handle (checkbox) element.
    }
}

/**
 * Helper to select and search documents.
 */
class BrowserHelper {

    /**
     * Create a new file browser support instance.
     *
     * @param {BrowserDocument[]} documents A list with all documents.
     *      This list is not checked and has to be perfectly valid.
     *      The objects of the list are modified to turn them into a tree structure.
     */
    constructor(documents) {
        this.documents = documents;  // the list with all documents.
        this.document_map = {};      // map the document identifiers to the documents.
        // build the map
        for (const doc of this.documents) {
            this.document_map[doc.index] = doc;
            doc.checkbox = document.getElementById(`node_${doc.index}_checkbox`);
            if (doc.index > 0) {
                doc.foldingHandle = document.getElementById(`node_${doc.index}_unfolded`);
                doc.foldingBox = document.getElementById(`node_${doc.index}_folding_box`);
            } else {
                doc.foldingHandle = null;
                doc.foldingBox = null;
            }
        }
        // build the tree
        for (const doc of this.documents) {
            if (doc.index > 0) {
                doc.parent = this.document_map[doc.parentIndex]
                doc.parent.children.push(doc)
            }
        }
        // Bind the methods to ensure `this` refers to the class instance
        this.onNodeCheckboxClick = this.onNodeCheckboxClick.bind(this);
        this.onFoldingHandleChange = this.onFoldingHandleChange.bind(this);
    }

    /**
     * Add all event listeners for the document browser.
     */
    addEventListeners() {
        for (const doc of this.documents) {
            const $checkbox = doc.checkbox;
            if ($checkbox) {
                $checkbox.addEventListener('click', this.onNodeCheckboxClick);
            }
            const $unfoldedCheckbox = doc.foldingHandle;
            if ($unfoldedCheckbox) {
                $unfoldedCheckbox.addEventListener('change', this.onFoldingHandleChange);
            }
        }
        const $selectAllButton = document.getElementById('browser_select_all');
        if ($selectAllButton) {
            $selectAllButton.addEventListener('click', (event) => {
                this.setNodeTreeChecked(0, true);
                event.preventDefault();
            })
        }
        const $selectNoneButton = document.getElementById('browser_select_none');
        if ($selectNoneButton) {
            $selectNoneButton.addEventListener('click', (event) => {
                this.setNodeTreeChecked(0, false);
                event.preventDefault();
            });
        }
    }

    onNodeCheckboxClick(event) {
        const checkbox = event.target;
        const nodeIndex = parseInt(checkbox.value);
        if (event.altKey) {
            setTimeout(() => {
                checkbox.checked = true;
            }, 10);
            this.setNodeTreeChecked(0, false);
            this.onSelectCheckboxChanged(nodeIndex, true);
            event.preventDefault();
        } else {
            const isChecked = checkbox.checked;
            this.onSelectCheckboxChanged(nodeIndex, isChecked);
        }
    }

    onFoldingHandleChange(event) {
        const checkbox = event.target;
        const nodeIndex = parseInt(checkbox.value);
        const isChecked = checkbox.checked;
        this.onUnfoldedCheckboxChanged(nodeIndex, isChecked);
    }

    /**
     * Called if a selection checkbox is toggled.
     *
     * @param {int} nodeIndex The node index.
     * @param {boolean} isChecked If the box is checked.
     */
    onSelectCheckboxChanged(nodeIndex, isChecked) {
        this.setNodeTreeChecked(nodeIndex, isChecked);
        let parentDoc = this.document_map[nodeIndex].parent;
        while (parentDoc) {
            let hasChecked = false;
            let hasUnchecked = false;
            for (const child of parentDoc.children) {
                if (child.checkbox.indeterminate) {
                    hasChecked = true;
                    hasUnchecked = true;
                    break;
                }
                if (child.checkbox.checked) {
                    hasChecked = true;
                    if (hasUnchecked) {
                        break;
                    }
                } else {
                    hasUnchecked = true;
                    if (hasChecked) {
                        break;
                    }
                }
            }
            if (hasChecked && hasUnchecked) {
                parentDoc.checkbox.indeterminate = true;
            } else if (hasChecked) {
                parentDoc.checkbox.indeterminate = false;
                parentDoc.checkbox.checked = true;
            } else {
                parentDoc.checkbox.indeterminate = false;
                parentDoc.checkbox.checked = false;
            }
            parentDoc = parentDoc.parent;
        }
        this.updateSelectionCount();
    }

    /**
     * Set a document selector and all its children to a checked state.
     *
     * @param {int} nodeIndex The node index
     * @param {boolean} isChecked If the box is checked.
     */
    setNodeTreeChecked(nodeIndex, isChecked) {
        const checkbox = this.document_map[nodeIndex].checkbox;
        checkbox.checked = isChecked;
        checkbox.indeterminate = false;
        for (const doc of this.document_map[nodeIndex].children) {
            this.setNodeTreeChecked(doc.index, isChecked);
        }
    }

    /**
     * Update the count of selected documents.
     */
    updateSelectionCount() {
        let count = 0;
        for (const doc of this.documents) {
            if (doc.isDocument && doc.checkbox.checked) {
                count += 1;
            }
        }
        const $p = document.getElementById('browser_select_count');
        $p.innerText = count.toString();
    }

    /**
     * If the user clicks on a node handle.
     *
     * @param {int} nodeIndex The node index.
     * @param {boolean} isChecked If the checkbox is checked = unfolded.
     */
    onUnfoldedCheckboxChanged(nodeIndex, isChecked) {
        const $foldingBox = this.document_map[nodeIndex].foldingBox;
        if (isChecked) {
            $foldingBox.classList.remove('is-hidden');
        } else {
            $foldingBox.classList.add('is-hidden');
        }
    }
}

export {BrowserHelper, BrowserDocument};
