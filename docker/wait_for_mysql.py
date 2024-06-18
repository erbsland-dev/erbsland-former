#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import time
import os
import sys

from MySQLdb import _mysql, OperationalError


def wait_for_mysql(timeout=300):
    start_time = time.time()
    db_config = {
        "host": "mariadb",
        "user": "erbsland_former",
        "password": os.environ.get("MARIADB_PASSWORD", ""),
        "database": "erbsland_former",
        "charset": "utf8mb4",
        "connect_timeout": 5,
    }
    print("Waiting for MySQL to be ready...")
    while True:
        try:
            connection = _mysql.connect(**db_config)
            time.sleep(1)
            connection.close()
            print("MySQL is ready!")
            break
        except OperationalError as e:
            if "connect" not in str(e):
                raise  # Stop on any other than connection errors.
            print(f"Error: {e}")
            print("MySQL is not ready yet. Waiting...")
            if time.time() - start_time >= timeout:
                print("Timeout: MySQL did not become ready in 5 minutes.")
                sys.exit(1)
            time.sleep(5)  # Wait for 5 seconds before retrying


if __name__ == "__main__":
    try:
        wait_for_mysql()
        exit(0)
    except Exception as e:
        exit(str(e))
