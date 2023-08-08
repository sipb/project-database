# Getting Set Up

## Development Work

For working on the project code, simply clone the repository to a local folder on your computer. 

Dependencies of this project includes: Python3, sqlalchemy, jinja2, django.

Getting a local dev environment working:

* When working in your local code environment, it's recommended to work off a Python 2 virtual environment (to ensure there's no compatibility issues with the SQLalchemy + dependencies versions).
  * To do so, on your first time run:
    * `sudo apt install libmysqlclient-dev` (Installs MySQL client)
    * `sudo apt-get install python-dev`
    * `python -m venv env` (Creates a local environment in current folder)
    * `source env/bin/activate` (Activates virtual environment)
    * `pip install -r requirements.txt` (Install necessary packages)
  * When you exit your workspace, remember to run: 
    * `deactivate`
  * Then, in the future, when you come back, simply do:
    * `source env/bin/activate`
    * **Note:** If you are using Visual Studio for your code editor, normally it will automatically load in your virtual environment (if found in current working directory) when you run your code. This saves time from having to load and unload your venv each time.
  * In addition, you will need to create a `creds.py` file inside the `web_scripts/` folder with the proper credentials. 
    * You can get a copy of the production credentials from the current projectDB maintainers. 
    * However, if you're adding a new capability with the backend (like a new schema or large modifications), it's recommended to populate creds.py with your own Scripts SQL credentials
  * Lastly, you will need to modify `schema.py` to have `SQL_URL` string format be:
      * `mysql+mysqlconnector://%s:%s@sql.mit.edu/%s?charset=utf8`
      * Make sure this change is done only for your local dev environment ONLY. This is necessary to get the code to work with your local MySQL connector library (along with specifying the correct charset), but this will not work if pushed to the Scripts server.
  
Alternatively, if you're having issues with package installations, you can also work on your code locally and then test it by deploying it your own Scripts locker and running it there. This option is more laborious (especially if you are making a lot of changes frequently):

* (Prerequisites) Register for Scripts locker by running 'add scripts' and 'scripts'. Also register for a Scripts SQL account. For more information see: <https://scripts.mit.edu/start/>

1. Create a working branch on the main repo
2. Edit code and commit to that branch
3. Clone the repo to your home folder on AFS
4. Run push.sh (check out the code before running it!)
5. Log into your Scripts account from AFS, usually `ssh [kerb]@scripts.mit.edu`
6. Create a `creds.py` file in the Scripts locker and populate it with the necessary permissions
    * When using the production credentials, make sure to set the OS environment variable `PROJECTS_DATABASE_MODE` in your Scripts locker to `test` (if using the testing database) or `prod` (if using the official database)
7. From there, you can run any of the project code file in isolation, like `python3 db.py`. You can also access the web-facing html pages at `[kerb].scripts.mit.edu/`