# Getting Set Up

## Development Work

For working on the project code, simply clone the repository to a local folder on your computer. 

Dependencies of this project includes: Python3, sqlalchemy, jinja2, django.

Unfortunately, due to the specialized environment in Scripts, the setup environment requires specific version of sqlalchemy (and its dependencies) to talk with the SQL backend, which we have not been able to reproduce in our local dev environments. If you want to test your code, the recommended way is to:

(Prerequisites) Register for Scripts locker by running 'add scripts' and 'scripts'. Also register for a Scripts SQL account. For more information see: <https://scripts.mit.edu/start/>

1. Create a working branch on the main repo
2. Edit code and commit to that branch
3. Clone the repo to your home folder on AFS
4. Run push.sh (check out the code before running it!)
5. Log into your Scripts account from AFS, usually `ssh [kerb]@scripts.mit.edu`
6. Create a `creds.py` file with the proper permission  
    * You can get a copy of the production credentials from the project maintainers. However, if you're adding a new capability with the backend, it's recommended to use your own SQL account
    * If using the production credentials, make sure to set the OS environment variable `PROJECTS_DATABASE_MODE` in your Scripts locker to `test` (if using the testing database) or `prod` (if using the official database)
7. From there, you can run any of the project code file in isolation, like `python3 db.py`. You can also access the web-facing html pages at `[kerb].scripts.mit.edu/`