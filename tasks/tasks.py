#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import time
from typing import Optional

from celery.exceptions import TaskError
from celery.utils.log import get_task_logger
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from tasks.actions import ActionBase
from tasks.actions.exception import ActionError, ActionStoppedByUser
from tasks.celery_app import app

logger = get_task_logger(__name__)


def get_task_object(task_id: str):
    """
    Get the task object. Wait up to 10 seconds until the object is available.

    :param task_id: The task ID
    :return: The task object.
    :except ActionError: If the task object can't be retrieved in time.
    """
    from tasks.models import Task

    for _ in range(20):
        try:
            return Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            pass
        time.sleep(0.5)
    raise ActionError("Task object was not ready in 10 seconds after the task started.")


@app.task(ignore_result=True, soft_time_limit=24 * 60 * 60, time_limit=24 * 60 * 60 + 60)
def run_task_action(task_id: str):
    """
    Run task that will perform the configured action.

    :param task_id: The task ID from the database
    """
    if not isinstance(task_id, str):
        raise TaskError("task_id must be a string.")

    from django.db import transaction
    from tasks.data_store import data_store
    from tasks.models import TaskStatus
    from tasks.models import TaskResult

    logger.debug(f"Starting task: {task_id}")
    action: Optional[ActionBase] = None
    try:
        logger.debug("Get the task object.")
        task = get_task_object(task_id)
    except ActionError as ex:
        logger.excepion(ex)
        return
    try:
        from tasks.actions.manager import action_manager

        logger.debug("Switch to running state.")
        with transaction.atomic():
            task.task_status = TaskStatus.RUNNING
            task.save()
        translation.activate(task.language_code)  # Activate the frontend language for the task.
        text = _("Starting %(subject)s") % {"subject": task.get_progress_subject()}
        data_store.update_task_progress(task_id, 0.0, {}, text)
        logger.debug(f"Create action instance for: {task.action}")
        action = action_manager.create_action(task.action, task_id, logger)
        logger.debug(f"Starting action")
        try:
            action.run(task.input_data)
            logger.debug(f"Successfully finished the action.")
            task_result = TaskResult.SUCCESS
            output_data = action.get_output_data()
            text = _("%(subject)s successfully finished") % {"subject": task.get_progress_subject()}
        except ActionStoppedByUser:
            logger.debug("The action was stopped by the user.")
            try:
                action.on_stopped()
            except Exception as error:
                logger.error(f"There was an exception raised in the `on_stopped()` call: {error}")
            task_result = TaskResult.STOPPED
            output_data = {}
            text = _("%(subject)s was stopped") % {"subject": task.get_progress_subject()}
        except ActionError as action_error:
            logger.debug(f"The action failed: {action_error}")
            try:
                action.on_failed(action_error)
            except Exception as error:
                logger.error(f"There was an exception raised in the `on_failed()` call: {error}")
            task_result = TaskResult.FAILURE
            output_data = action.get_output_data()
            text = _("%(subject)s failed: %(message)s") % {
                "subject": str(task.get_progress_subject()),
                "message": str(action_error.message),
            }

        logger.debug(f"Writing task result: {task_result} - {text}")
        with transaction.atomic():
            task.task_status = TaskStatus.FINISHED
            task.task_result = task_result
            task.output_data = output_data
            task.save()
        next_url = task.get_next_url()
        data_store.set_task_finished(task_id, task_result, {}, text, next_url)
        logger.debug(f'Finished task: {task_id} with result="{task_result}" text="{text}" next_url="{next_url}"')

    except Exception as ex:
        logger.debug(f"Unexpected exception for task {task_id}: {ex}")
        if action:
            try:
                action.on_failed(ex)
            except Exception as error:
                logger.error(f"There was an exception raised in the `on_failed()` call: {error}")
                logger.excepion(error, stack_info=True)
        text = _("The task failed with an unexpected problem: %(message)s") % {"message": str(ex)}
        try:
            data_store.set_task_finished(task_id, TaskResult.FAILURE, {}, text, task.failure_url)
        except Exception as error:
            # If the problem was the connection to the data store, ignore it, but log it.
            logger.excepion(error, stack_info=True)
        output_data = {"status": "failed", "reason": str(ex)}
        with transaction.atomic():
            task.task_status = TaskStatus.FINISHED
            task.task_result = TaskResult.FAILURE
            task.output_data = output_data
            task.save()
        logger.debug(
            f'Finished task: {task_id} with result="{task.task_result.name}" '
            f'text="{text}" next_url="{task.get_next_url()}"'
        )
        logger.debug(f"Passing exception to system.")
        raise ex
