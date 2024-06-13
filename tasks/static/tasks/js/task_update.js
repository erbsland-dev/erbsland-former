/*
 * Copyright © 2023 Tobias Erbsland. Web: https://erbsland.dev/
 * Copyright © 2023 EducateIT GmbH. Web: https://educateit.ch/
 *
 * This program is free software: you can redistribute it and/or modify it under the terms of the
 * GNU Lesser General Public License as published by the Free Software Foundation, either
 * version 3 of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 * See the GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License along with this program.
 * If not, see <https://www.gnu.org/licenses/>.
 */


'use strict';


class TaskStatusHandler {

    /**
     * Constructor for a TaskStatusHandler object.
     *
     * @param {string} taskId - The ID of the task.
     * @param {string} csrfToken - The CSRF token for authentication.
     * @param {string} apiUrl - The URL of the API where to get the status information from.
     */
    constructor(taskId, csrfToken, apiUrl) {
        this.taskId = taskId;
        this.csrfToken = csrfToken;
        this.apiUrl = apiUrl;
        this.statusInfoMap = {
            'created': {
                'progressBarClass': 'progress is-success',
                'textClass': '',
                'statusText': gettext('Waiting for Start'),
                'statusClass': '',
            },
            'running': {
                'progressBarClass': 'progress is-success',
                'textClass': '',
                'statusText': gettext('Running'),
                'statusClass': '',
            },
            'finished|success': {
                'progressBarClass': 'progress is-primary',
                'textClass': '',
                'statusText': gettext('Successfully Finished'),
                'statusClass': '',
            },
            'finished|stopped': {
                'progressBarClass': 'progress is-danger',
                'textClass': 'is-danger',
                'statusText': gettext('Stopped'),
                'statusClass': 'is-danger',
            },
            'finished|failure': {
                'progressBarClass': 'progress is-danger',
                'textClass': 'is-danger',
                'statusText': gettext('Failed'),
                'statusClass': 'is-danger',
            },
            'api_error': {
                'progressBarClass': 'progress is-danger',
                'textClass': 'is-danger',
                'statusText': gettext('Unexpected Problem'),
                'statusClass': 'is-danger',
            },
            'stopping': {
                'progressBarClass': 'progress is-danger',
                'textClass': 'is-danger',
                'statusText': gettext('Waiting for Stop'),
                'statusClass': 'is-danger',
            },
        };

        // DOM elements
        const taskElement = document.getElementById(`task_${this.taskId}`);
        this.taskStatus = taskElement.getElementsByClassName('task-status')[0];
        this.taskText = taskElement.getElementsByClassName('task-text')[0];
        this.progressBar = taskElement.getElementsByClassName('progress')[0];
        this.taskStatusFields = taskElement.getElementsByClassName('task-status-fields')[0];
        this.stopOpenButton = taskElement.getElementsByClassName('task-stop-open')[0];
        this.stopButton = taskElement.getElementsByClassName('task-stop')[0];
        this.continueButton = taskElement.getElementsByClassName('task-continue')[0];
        this.reloadButton = taskElement.getElementsByClassName('task-reload')[0];
        this.stopButton.addEventListener('click', (event) => {
            event.preventDefault();
            this.onStopClicked()
        });
        this.sendStatusRequest();
    };

    /**
     * Updates the status, progress, and text of the task.
     *
     * @param {string} status - The status of the task.
     * @param {number} progress - The progress of the task.
     * @param {object} statusFields - The status fields for the task
     * @param {string} text - The text to be displayed for the task.
     */
    #updateStatus(status, progress, statusFields, text) {
        const statusInfo = this.statusInfoMap[status];
        this.taskStatus.textContent = statusInfo['statusText'];
        const statusClass = statusInfo['statusClass'];
        this.taskStatus.className = `block has-text-weight-bold task-status ${statusClass}`;
        this.taskText.textContent = text;
        const textClass = statusInfo['textClass'];
        this.taskText.className = `block task-text ${textClass}`;
        this.progressBar.value = progress;
        this.progressBar.textContent = `${progress}%`;
        this.progressBar.className = statusInfo['progressBarClass'];
        for (const [key, value] of Object.entries(statusFields)) {
            let cells = this.taskStatusFields.getElementsByClassName(`field-${key}`);
            try {
                if (cells) {
                    let cell = cells[0];
                    cell.textContent = value;
                }
            } catch (e) {
                // ignore any errors assigning status fields.
            }
        }
    };

    /**
     * Handles the `onStopClicked` event.
     * Updates button text and status, then sends a request to the stop URL.
     */
    onStopClicked() {
        this.stopButton.classList.add('is-loading');
        this.sendStopRequest();
    };

    /**
     * Handle the response from a fetch request.
     *
     * @param {Response} response - The response object from the fetch request.
     * @throws {Error} - If the response is not OK (status code is not in the 200 range).
     * @return {Promise} - A Promise that resolves to the JSON representation of the response.
     */
    handleStatusResponse(response) {
        if (!response.ok) {
            throw new Error(gettext('Failed to fetch the task status.'));
        }
        return response.json();
    };

    /**
     * Handle the status data received from the interface.
     *
     * The received data is a JSON document with this format:
     * ```json
     * {
     *  'status': 'finished',
     *  'result': 'success',
     *  'progress': 100,
     *  'text': 'Successfully finished ...',
     *  'next_url': '/example/url/'
     * }
     * ```
     *
     * @param {Promise} data The received data.
     * @param {string} data.status The status, e.g. `running`, `finished` ...
     * @param {string} data.result The result when a task is finished.
     * @param {int} data.progress The progress in percent 0-100.
     * @param {string} data.status_values The status values.
     * @param {string} data.text The current task that is worked on as text.
     * @param {string} data.next_url When finished, an optional URL to jump to.
     * @param {boolean} data.stop_requested If the user requested to stop the operation.
     */
    handleStatusData(data) {
        console.log(data)
        let combinedStatus = data.status + (data.result !== 'none' ? `|${data.result}` : '');
        if (data.status !== 'finished' && data.stop_requested) {
            combinedStatus = 'stopping';
        }
        if (!Object.keys(this.statusInfoMap).includes(combinedStatus)) {
            throw new Error(`Got an unexpected status value when fetching the task status. value=${combinedStatus}`);
        }
        if (data.status === 'finished') {
            this.stopOpenButton.classList.add('is-hidden');
            this.continueButton.classList.remove('is-hidden');
            if (data.next_url) {
                this.continueButton.href = data.next_url;
            }
            if (data.result === 'success') {
                if (data.next_url) {
                    // Delay continue to give the browser time to render the last status update.
                    setTimeout(function () {
                        window.location.href = data.next_url;
                    }, 1000);
                }
            } else if (data.result === 'stopped') {
                this.continueButton.classList.remove('is-success');
                this.continueButton.classList.add('is-danger');
            } else {
                this.continueButton.classList.remove('is-success');
                this.continueButton.classList.add('is-danger');
            }
        } else {
            setTimeout(this.sendStatusRequest.bind(this), 1000);
        }
        this.#updateStatus(combinedStatus, data.progress, data.status_values, data.text);
    };

    /**
     * Handles an error by updating the status, task text element, and task button element.
     *
     * @param {Error} error - The error that occurred.
     */
    handleStatusError(error) {
        console.error(error)
        this.reloadButton.classList.remove('is-hidden');
        this.stopOpenButton.classList.add('is-hidden');
        this.continueButton.classList.add('is-hidden');
        this.#updateStatus('api_error', 100, {}, gettext('Could not fetch the current task status.'));
    };

    /**
     * Handle the stop data received from the interface.
     *
     * @param {Promise} data The received data.
     * @param {string} data.status The status, e.g. `stopping` ...
     */
    handleStopData(data) {
        if (data.status !== 'stopping') {
            throw new Error(`Got an unexpected status value when trying to stop the process.`);
        }
    }

    /**
     * Handles a error after a stop request.
     */
    handleStopError(error) {
        console.error(error)
        this.reloadButton.classList.remove('is-hidden');
        this.stopOpenButton.classList.add('is-hidden');
        this.continueButton.classList.add('is-hidden');
        this.#updateStatus('api_error', 100, {}, gettext('Failed to stop the current task.'));
    }

    /**
     * Creates a new Request object with the provided action.
     *
     * @param {string} action - The action to be performed.
     * @returns {Request} A new Request object configured with the provided action.
     */
    #createRequest(action) {
        const data = {
            'action': action,
            'task_id': this.taskId
        }
        return new Request(
            this.apiUrl,
            {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.csrfToken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data),
                mode: 'same-origin'
            }
        )
    }

    /**
     * Close all modal forms.
     */
    closeAllModals() {
        (document.querySelectorAll('.modal') || []).forEach(($modal) => {
            $modal.classList.remove('is-active');
        });
    }

    /**
     * Handle the response from a fetch request.
     *
     * @param {Response} response - The response object from the fetch request.
     * @throws {Error} - If the response is not OK (status code is not in the 200 range).
     * @return {Promise} - A Promise that resolves to the JSON representation of the response.
     */
    handleStopResponse(response) {
        this.stopButton.classList.remove('is-loading');
        this.closeAllModals();
        if (!response.ok) {
            throw new Error(gettext('Failed to fetch the stop request status.'));
        }
        return response.json();
    };


    /**
     * Send a new status request to the API
     */
    sendStatusRequest() {
        const request = this.#createRequest('status');
        fetch(request)
            .then(response => this.handleStatusResponse(response))
            .then(data => this.handleStatusData(data))
            .catch(error => this.handleStatusError(error));
    };

    /**
     * Send a new stop request to the API.
     */
    sendStopRequest() {
        const request = this.#createRequest('stop');
        fetch(request)
            .then(response => this.handleStopResponse(response))
            .then(data => this.handleStopData(data))
            .catch(error => this.handleStopError(error));
    }
}

