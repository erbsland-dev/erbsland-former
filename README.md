ErbslandFORMER
==============

*ErbslandFORMER* is designed to efficiently edit and manage large volumes of text through both automated and manual processes. It organizes text into documents and fragments, ensuring optimal splitting points based on text format for more manageable editing.

Edits are facilitated by various specialized tools, ranging from simple regular expressions to advanced large language models like OpenAI's ChatGPT. Each edit is tracked per fragment, and users can review and approve changes using a detailed diff view.

With a robust revision system, ErbslandFORMER allows you to track changes incrementally, making it easy to revert to previous versions. This ensures that you can save snapshots of your projects before and after processing.

Finally, the transformed text can be seamlessly exported and reintegrated into its original source.

*Please note: This project is in beta phase, so some information in this document may be outdated.*

Features
--------

- Project, document, and document fragment-based text organization.
- Automatic splitting into appropriately sized fragments for various tasks, based on units like LLM tokens, characters, words, lines, or bytes.
- Special split point handling for formats such as Markdown, C/C++, Python, and plain text.
- Simple revision system for incremental project transformation.
- Integrated LLM processor using OpenAI's API, supporting models like GPT-4o, GPT-4 and GPT-3.5.
- Integrated regular expression processor for pattern-based document transformation.
- Import and export capabilities for single documents or ZIP files with folder structures.

Requirements
------------

This application consists of a frontend, a Django/WSGI application, a database, and a backend that executes tasks in separate threads. The following are required:

- **Python 3.12+**

  The application is written for Python 3.12 or newer and requires the packages listed in `requirements.txt` or `requirements.in`. While the listed versions are tested, you may update them to the latest versions if needed.

- **Apache or nginx: Webserver to run a WSGI application**

  A web server or proxy, like Apache or nginx, is required to run the frontend application. Refer to the documentation for setting up your chosen web service for a WSGI application. For testing purposes, you can use Django's built-in web server.

- **Redis: Message Broker for Celery and the Frontend**

  Redis is necessary as a message broker for Celery to handle background tasks that may take extensive time to complete. Redis also facilitates communication between running tasks and the web interface to display progress and logs.

- **MariaDB/MySQL/Postgres Database**

  A database like MySQL, MariaDB, or Postgres is needed to store all processed data. For handling large amounts of data, ensure your database installation is appropriately scaled. You may also consider moving the text content table to a specialized database for better performance.

License and Copyright
---------------------

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.

See document [COPYRIGHT.md](COPYRIGHT.md) for details.
