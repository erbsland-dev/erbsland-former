
.. index::
    single: Installation; Update

============================
Update Existing Installation
============================

Updating a local installation of the *ErbslandFORMER* application requires a few straightforward steps. Follow the instructions below to ensure a smooth update process.

1. **Stop the Apache Web Server**

   Connect to the server and stop the Apache web server.

   .. code-block:: console

       test@erbsland-former:~$ sudo systemctl stop apache2

2. **Switch to the Application User and Navigate to the Application Directory**

   Change to the application user and set the current directory to the application directory.

   .. code-block:: console

       test@erbsland-former:~$ sudo su erbsland_former
       erbsland_former@erbsland-former:/home/test$ cd /var/www/erbsland-former/app/
       erbsland_former@erbsland-former:/var/www/erbsland-former/app$ █

3. **Activate the Python Virtual Environment**

   Activate the Python virtual environment.

   .. code-block:: console

       $ source /var/www/erbsland-former/venv/bin/activate
       $ █

4. **Stash Any Local Changes**

   If there are any local changes, make sure to stash them.

   .. code-block:: console

       $ git stash
       Saved working directory and index state WIP on main: 7c66a87 Preparation for release version.
       $ █

5. **Pull the Latest Version of the Application**

   Pull the latest version of the application from the repository.

   .. code-block:: console

       $ git pull
       Updating a1d1368..7c66a87
       Fast-forward
       (...)
       $ █

6. **Reapply Stashed Changes (If Any)**

   If you have stashed any changes, re-apply them and remove the stash.

   .. code-block:: console

       $ git stash pop
       (...)
       $ █

7. **Set the Environment Variable for Custom Settings**

   Set the environment variable for your custom settings module.

   .. code-block:: console

       $ export DJANGO_SETTINGS_MODULE=ErbslandFormer.my_settings
       $ █

8. **Update Static Files**

   Update the static files. In most cases, nothing will change.

   .. code-block:: console

       $ python manage.py collectstatic

       You have requested to collect static files at the destination
       location as specified in your settings:

           /var/www/erbsland-former/static

       This will overwrite existing files!
       Are you sure you want to do this?

       Type 'yes' to continue, or 'no' to cancel: yes

       3 static files copied to '/var/www/erbsland-former/static', 186 unmodified.
       $ █

9. **Migrate the Database**

   Migrate the database. In most cases, there are no migrations required.

   .. code-block:: console

       $ python manage.py migrate
       (...)
       $ █

10. **Exit the Application User Shell and Restart Apache**

    Exit the application user shell and restart Apache.

    .. code-block:: console

        (venv) erbsland_former@erbsland-former:/var/www/erbsland-former/app$ exit
        test@erbsland-former:~$ sudo systemctl start apache2
        test@erbsland-former:~$ █

You have now successfully updated your *ErbslandFORMER* application.