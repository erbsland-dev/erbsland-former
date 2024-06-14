// Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch
// According to the copyright terms specified in the file "COPYRIGHT.md".
// SPDX-License-Identifier: GPL-3.0-or-later

import {
    crosshairCursor,
    drawSelection,
    dropCursor,
    EditorView,
    highlightActiveLine,
    highlightActiveLineGutter,
    highlightSpecialChars,
    keymap,
    lineNumbers,
    rectangularSelection,
} from "@codemirror/view";
import {defaultKeymap, history, historyKeymap, indentWithTab} from "@codemirror/commands";
import {
    bracketMatching,
    defaultHighlightStyle,
    foldGutter,
    foldKeymap,
    indentOnInput,
    syntaxHighlighting
} from "@codemirror/language";
import {markdown} from "@codemirror/lang-markdown";
import {python} from "@codemirror/lang-python";
import {cpp} from "@codemirror/lang-cpp";
import {EditorState} from "@codemirror/state";
import {lintKeymap} from "@codemirror/lint";
import {highlightSelectionMatches, searchKeymap} from '@codemirror/search';
import {autocompletion, closeBrackets, closeBracketsKeymap, completionKeymap} from '@codemirror/autocomplete';

export {EditorView} from '@codemirror/view';


/**
 * Loads the language based on the given syntax format for the code editor.
 *
 * @param {string} syntax_format - The syntax format of the language to load.
 * @return {LanguageSupport|null} - The corresponding language object, or `null` if no matching language is found.
 */
function loadLanguage(syntax_format) {
    switch (syntax_format) {
        case 'markdown':
            return markdown();
        case 'python':
            return python();
        case 'cpp':
            return cpp();
        default:
            return null;
    }
}


/**
 * Converts a base64 string to a Uint8Array of bytes.
 *
 * @param {string} base64 - The base64 string to convert to bytes.
 * @return {Uint8Array} - The Uint8Array of bytes representing the base64 string.
 */
function base64ToBytes(base64) {
    const binString = atob(base64);
    return Uint8Array.from(binString, (m) => m.codePointAt(0));
}


/**
 * Create a new editor instance.
 *
 * @param {HTMLElement} parent_element - The parent element to attach the editor to.
 * @param {object} data - The data for the editor.
 * @returns {EditorView} - The created editor view instance.
 */
function createEditor(parent_element, data) {
    const initialText = new TextDecoder().decode(base64ToBytes(data.initial_text_base64));
    const firstLineNumber = data.first_line_number;
    const lineNumbersEnabled = data.line_numbers_enabled;
    const syntaxFormat = data.syntax_format;

    function lineNumberFormat(lineNo, state) {
        return String(lineNo + firstLineNumber - 1).padStart(5, ' ');
    }

    let extensions = [
        highlightActiveLineGutter(),
        highlightSpecialChars(),
        // highlightWhitespace(),
        // highlightTrailingWhitespace(),
        history(),
        foldGutter(),
        drawSelection(),
        dropCursor(),
        EditorState.allowMultipleSelections.of(true),
        EditorState.tabSize.of(4),
        EditorState.lineSeparator.of("\n"),
        EditorView.lineWrapping,
        indentOnInput(),
        syntaxHighlighting(defaultHighlightStyle, {fallback: true}),
        bracketMatching(),
        closeBrackets(),
        autocompletion(),
        rectangularSelection(),
        crosshairCursor(),
        highlightActiveLine(),
        highlightSelectionMatches(),
        keymap.of([
            ...closeBracketsKeymap,
            ...defaultKeymap,
            ...searchKeymap,
            ...historyKeymap,
            ...foldKeymap,
            ...completionKeymap,
            ...lintKeymap,
            indentWithTab
        ]),
    ];
    if (lineNumbersEnabled) {
        extensions.push(lineNumbers({formatNumber: lineNumberFormat}));
    }
    const lang = loadLanguage(syntaxFormat);
    if (lang) {
        extensions = [...extensions, lang];
    }
    return new EditorView({
        doc: initialText,
        extensions: extensions,
        parent: parent_element,
        lineWrapping: true,
    });
}


/**
 * Registers an editor for a specific field.
 *
 * Assumes there is an `input` and `div` element with the id's "code_editor_[field name]_field" and
 * the `div` with "code_editor_[field_name]" in the document.
 *
 * @param {string} editor_id - The ID of the editor element.
 * @param {string} hidden_field_id - The ID of the hidden field to submit the editor data.
 * @param {object} data - The configuration of the editor and its initial text.
 */
function registerEditor(editor_id, hidden_field_id, data) {
    const parentElement = document.getElementById(editor_id);
    const removed_last_newline = data.removed_last_newline
    const editor = createEditor(parentElement, data);
    const input = document.getElementById(hidden_field_id);
    const form = parentElement.closest('form');
    form.addEventListener('submit', () => {
        let text = editor.state.doc.toString();
        if (removed_last_newline === true) {
            text += '\n';
        }
        input.value = text;
    });
}


export {createEditor, registerEditor};

