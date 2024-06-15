.. _settings:
.. index::
    !single: Settings

==================
Settings Reference
==================

Backend
=======

.. index::
    !single: BACKEND_ENCRYPTION_KEY
    single: Settings; BACKEND_ENCRYPTION_KEY

BACKEND_ENCRYPTION_KEY
----------------------

**Default:** ""

The ``BACKEND_ENCRYPTION_KEY`` is used to synchronously encrypt and decrypt sensitive user settings. This key ensures that all sensitive data, such as passwords and API keys, are securely stored. Make sure to set this key to a secure, random string to maintain the integrity of your data.

.. index::
    !single: BACKEND_ENCRYPTION_KEY_FALLBACKS
    single: Settings; BACKEND_ENCRYPTION_KEY_FALLBACKS

BACKEND_ENCRYPTION_KEY_FALLBACKS
--------------------------------

**Default:** []

The ``BACKEND_ENCRYPTION_KEY_FALLBACKS`` is a list of fallback encryption keys. These keys are used to decrypt data that was encrypted with a previous encryption key. When you rotate the encryption key, add the old key to this list to ensure that existing data can still be decrypted. Note that user settings encrypted with fallback keys will not be automatically migrated to the new key without user interaction. Provide users sufficient time to update their passwords and API keys before removing an old key from this list.

.. index::
    !single: BACKEND_IGNORE_SYNTAX_HANDLER
    single: Settings; BACKEND_IGNORE_SYNTAX_HANDLER

BACKEND_IGNORE_SYNTAX_HANDLER
-----------------------------

**Default:** []

The ``BACKEND_IGNORE_SYNTAX_HANDLER`` specifies a list of syntax handler identifiers that should be ignored by the backend. This setting is useful for excluding certain syntax handlers that are not needed or might cause conflicts.

.. index::
    !single: BACKEND_DEFAULT_SYNTAX_HANDLER
    single: Settings; BACKEND_DEFAULT_SYNTAX_HANDLER

BACKEND_DEFAULT_SYNTAX_HANDLER
------------------------------

**Default:** "markdown"

The ``BACKEND_DEFAULT_SYNTAX_HANDLER`` sets the default syntax handler to be used by the application. The default value is "markdown". This handler processes and converts text according to the specified syntax rules.

.. index::
    !single: BACKEND_IGNORE_SIZE_CALCULATOR
    single: Settings; BACKEND_IGNORE_SIZE_CALCULATOR

BACKEND_IGNORE_SIZE_CALCULATOR
------------------------------

**Default:** []

The ``BACKEND_IGNORE_SIZE_CALCULATOR`` contains a list of size calculator identifiers that should be ignored. Size calculators determine the size of data for various operations. Use this setting to exclude specific size calculators that are unnecessary for your application.

.. index::
    !single: BACKEND_TRANSFORMER
    single: Settings; BACKEND_TRANSFORMER

BACKEND_TRANSFORMER
-------------------

**Default:** ["regex_transformer.transformers.RegexTransformer", "openai_transformer.transformers.OpenAiTransformer"]

The ``BACKEND_TRANSFORMER`` is a list of active transformer classes used to process and transform data. This list includes default transformers like `RegexTransformer` and `OpenAiTransformer`. You can extend this list with custom transformers or remove the ones you do not need.

.. index::
    !single: BACKEND_DEFAULT_SIZE_CALCULATOR
    single: Settings; BACKEND_DEFAULT_SIZE_CALCULATOR

BACKEND_DEFAULT_SIZE_CALCULATOR
-------------------------------

**Default:** "char"

The ``BACKEND_DEFAULT_SIZE_CALCULATOR`` sets the default size calculator for the application. The default calculator measures data size in characters. You can change this to other units of measurement as required by your application.

.. index::
    !single: BACKEND_INGEST_UPLOAD_FILE_SIZE
    single: Settings; BACKEND_INGEST_UPLOAD_FILE_SIZE

BACKEND_INGEST_UPLOAD_FILE_SIZE
-------------------------------

**Default:** 10_000_000

The ``BACKEND_INGEST_UPLOAD_FILE_SIZE`` defines the maximum allowable size for uploaded data, in bytes. The default limit is set to 10,000,000 bytes (approximately 10 MB). Adjust this value according to your application's requirements and server capacity.


.. index::
    !single: BACKEND_INGEST_DOCUMENT_SIZE
    single: Settings; BACKEND_INGEST_DOCUMENT_SIZE

BACKEND_INGEST_DOCUMENT_SIZE
----------------------------

**Default:** 10_000_000

The ``BACKEND_INGEST_DOCUMENT_SIZE`` specifies the maximum size for a single document, either uploaded or extracted, in bytes. The default value is 10,000,000 bytes (approximately 10 MB). This limit helps manage storage and processing requirements.

.. index::
    !single: BACKEND_INGEST_FILE_COUNT
    single: Settings; BACKEND_INGEST_FILE_COUNT

BACKEND_INGEST_FILE_COUNT
-------------------------

**Default:** 100

The ``BACKEND_INGEST_FILE_COUNT`` sets the maximum number of files that can be imported in a single upload session. The default limit is 100 files. Adjust this number based on your application's needs and server capabilities.

.. index::
    !single: BACKEND_WORKING_DIR
    single: Settings; BACKEND_WORKING_DIR

BACKEND_WORKING_DIR
-------------------

**Default:** "[project]/working_dir"

The ``BACKEND_WORKING_DIR`` specifies the directory where temporary files are created during the import and export processes to and from the database. This directory must have read and write access for both the frontend and backend processes. It is crucial that this directory is not publicly accessible via the web server, as it is not intended to serve as a public ``MEDIA`` directory.

.. index::
    !single: BACKEND_SIZE_CALCULATION_MAX_BLOCK_SIZE
    single: Settings; BACKEND_SIZE_CALCULATION_MAX_BLOCK_SIZE

BACKEND_SIZE_CALCULATION_MAX_BLOCK_SIZE
---------------------------------------

**Default:** 200_000

The ``BACKEND_SIZE_CALCULATION_MAX_BLOCK_SIZE`` setting defines the maximum size of a block of data held in memory for size calculations. Individual size calculation modules can lower this value further but cannot increase this limit. This ensures that the memory usage for size calculations is controlled and optimized.

Tasks System
============

The settings module for the "tasks" application includes configurations for the Celery system and Redis. Use keys prefixed with ``TASKS_CELERY_*`` to configure Celery. Redis serves as the broker for Celery, as well as for real-time task updates and logs. Ensure that Celery (``TASKS_CELERY_...``) and the application (``TASKS_DATA_REDIS_...``) do not share the same Redis instance or database.

.. index::
    !single: TASKS_CELERY_BROKER_URL
    single: Settings; TASKS_CELERY_BROKER_URL

TASKS_CELERY_BROKER_URL
-----------------------

**Default:** "redis://127.0.0.1/"

The ``TASKS_CELERY_BROKER_URL`` setting specifies the URL of the broker used by the Celery application. By default, it uses a local Redis instance. Adjust this URL according to your broker setup if you are using a different broker or hosting Redis remotely.

.. index::
    !single: TASKS_CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP
    single: Settings; TASKS_CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP

TASKS_CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP
-----------------------------------------------

**Default:** True

The ``TASKS_CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP`` setting determines whether Celery should retry connecting to the broker on startup if the initial connection attempt fails. The default value is `True`, which helps ensure that temporary network issues do not prevent Celery from starting.

.. index::
    !single: TASKS_CELERY_TASK_SOFT_TIME_LIMIT
    single: Settings; TASKS_CELERY_TASK_SOFT_TIME_LIMIT

TASKS_CELERY_TASK_SOFT_TIME_LIMIT
---------------------------------

**Default:** 24 * 60 * 60

The ``TASKS_CELERY_TASK_SOFT_TIME_LIMIT`` setting specifies the maximum time, in seconds, that a task is allowed to run before a soft timeout occurs. The default value is 24 hours. This soft limit allows tasks to handle cleanup operations before being forcibly terminated.

.. index::
    !single: TASKS_CELERY_TASK_TIME_LIMIT
    single: Settings; TASKS_CELERY_TASK_TIME_LIMIT

TASKS_CELERY_TASK_TIME_LIMIT
----------------------------

**Default:** 24 * 60 * 60 + 60

The ``TASKS_CELERY_TASK_TIME_LIMIT`` setting specifies the hard timeout for a task, which is the maximum time in seconds a task is allowed to run, including an additional 60 seconds after the soft timeout. The default value is 24 hours and 60 seconds. This ensures that tasks do not run indefinitely and are terminated if they exceed the soft timeout.

.. index::
    !single: TASKS_DATA_REDIS_HOST
    single: Settings; TASKS_DATA_REDIS_HOST

TASKS_DATA_REDIS_HOST
---------------------

**Default:** "127.0.0.1"

The ``TASKS_DATA_REDIS_HOST`` setting specifies the hostname or IP address of the Redis server used by the tasks system. By default, it points to a local Redis instance. Update this value if your Redis server is hosted remotely or has a different hostname.

.. index::
    !single: TASKS_DATA_REDIS_PORT
    single: Settings; TASKS_DATA_REDIS_PORT

TASKS_DATA_REDIS_PORT
---------------------

**Default:** 6379

The ``TASKS_DATA_REDIS_PORT`` setting specifies the port on which the Redis server for the tasks system is running. The default value is 6379, which is the standard port for Redis. Change this value if your Redis server uses a different port.

.. index::
    !single: TASKS_DATA_REDIS_DB_NUM
    single: Settings; TASKS_DATA_REDIS_DB_NUM

TASKS_DATA_REDIS_DB_NUM
-----------------------

**Default:** 1

The ``TASKS_DATA_REDIS_DB_NUM`` setting specifies the database number used by Redis for the tasks system. Redis allows multiple databases to be used on the same server instance, identified by an index number. The default value is 1. Ensure that this value does not conflict with other applications using the same Redis instance.

AI Transformer
==============

.. index::
    !single: AI_API_KEY
    single: Settings; AI_API_KEY

AI_API_KEY
----------

**Default:** ""

The ``AI_API_KEY`` setting is used to configure the API key required to authenticate with the OpenAI API. This key is set globally and is shared by all users of the server. Ensure that you keep this key secure and do not expose it publicly. Obtain this key from the OpenAI platform and set it here to enable AI functionalities.

.. index::
    !single: AI_ORGANIZATION_ID
    single: Settings; AI_ORGANIZATION_ID

AI_ORGANIZATION_ID
------------------

**Default:** ""

The ``AI_ORGANIZATION_ID`` setting specifies the organization ID associated with your OpenAI account. This ID is used globally for all users on the server. It helps in organizing and managing access within a team or company structure. Set this ID to ensure proper tracking and billing under the correct organization.

.. index::
    !single: AI_PROJECT_ID
    single: Settings; AI_PROJECT_ID

AI_PROJECT_ID
-------------

**Default:** ""

The ``AI_PROJECT_ID`` setting defines the project ID for your OpenAI API usage. This ID is also set globally for all users and helps in categorizing API usage under specific projects. This is useful for tracking and managing usage costs and performance metrics for different projects.

.. index::
    !single: AI_BASE_URL
    single: Settings; AI_BASE_URL

AI_BASE_URL
-----------

**Default:** "https://api.openai.com/v1/"

The ``AI_BASE_URL`` setting specifies the base URL for the OpenAI API. This URL is used as the endpoint for all API requests made by the application. The default value is set to the official OpenAI API endpoint. Modify this URL only if you are using a custom or internal API endpoint.

.. index::
    !single: AI_ALLOW_USER_OVERRIDES
    single: Settings; AI_ALLOW_USER_OVERRIDES

AI_ALLOW_USER_OVERRIDES
-----------------------

**Default:** True

The ``AI_ALLOW_USER_OVERRIDES`` setting determines whether individual users can override the globally configured API key and organization ID with their own values. If set to `True`, users can provide their own API credentials, which will be used instead of the global settings. This flexibility allows users to test or use their own OpenAI accounts without affecting the global configuration.

.. index::
    !single: AI_ALLOWED_MODELS
    single: Settings; AI_ALLOWED_MODELS

AI_ALLOWED_MODELS
-----------------

**Default:** []

The ``AI_ALLOWED_MODELS`` setting specifies which language models from the OpenAI interface are available for users to select. When this list is empty, all implemented models can be used. To restrict access to certain models, provide a list of allowed model identifiers (e.g., "gpt-3.5-turbo"). This can be useful for controlling costs and ensuring that only approved models are utilized within the application.