AI-FACILITATED FARM PRODUCE HARVESTING MANAGEMENT SYSTEM
Case Study: Faculty of Agriculture, University of Ibadan
----------------------------------------------------------

HOW TO DEPLOY ON PYTHONANYWHERE (FREE, NO CODING REQUIRED)
=============================================================

STEP 1 — Create a free account
  Go to https://www.pythonanywhere.com and sign up for a free "Beginner" account.

STEP 2 — Upload this project
  1. Once logged in, click "Files" at the top.
  2. Create a new folder called "harvestms".
  3. Upload this entire zip file into your PythonAnywhere home directory.
  4. Open a "Bash console" (click "Consoles" > "Bash") and run:
       unzip harvestms_project.zip -d harvestms
       cd harvestms

STEP 3 — Create a virtual environment and install requirements
  In the same Bash console, run:
       mkvirtualenv --python=python3.12 harvestms-env
       pip install -r requirements.txt

  (If mkvirtualenv is not available, use:
       python3.12 -m venv harvestms-env
       source harvestms-env/bin/activate
       pip install -r requirements.txt )

STEP 4 — Set up the database
  Still in the Bash console (inside the harvestms folder, virtualenv active):
       python manage.py migrate
       python manage.py createsuperuser
  Follow the prompts to create your admin login.

STEP 4.5 — Load sample demo data (recommended for your Chapter 4 screenshots)
       python manage.py loaddata sample_data
       python manage.py loaddata sample_predictions
  This loads a "Maize" crop profile, a registered plot, 3 historical
  harvest records, and one AI prediction, so you can demonstrate every
  screen (including Stage 2 of the AI module) immediately.

STEP 5 — Create the Web App
  1. Go to the "Web" tab > "Add a new web app".
  2. Choose "Manual configuration" (NOT the Django wizard) > Python 3.12.
  3. Under "Code":
       - Source code: /home/YOURUSERNAME/harvestms
       - Working directory: /home/YOURUSERNAME/harvestms
  4. Under "Virtualenv": enter the path to the virtualenv you created
       (e.g. /home/YOURUSERNAME/.virtualenvs/harvestms-env)
  5. Click the WSGI configuration file link and REPLACE its content with:

       import sys
       path = '/home/YOURUSERNAME/harvestms'
       if path not in sys.path:
           sys.path.append(path)
       import os
       os.environ['DJANGO_SETTINGS_MODULE'] = 'harvestms.settings'
       os.environ['DEBUG'] = 'False'
       os.environ['ALLOWED_HOSTS'] = 'YOURUSERNAME.pythonanywhere.com'
       from django.core.wsgi import get_wsgi_application
       application = get_wsgi_application()

     (Replace YOURUSERNAME with your actual PythonAnywhere username, twice.)

  6. Under "Static files", add:
       URL: /static/   ->   Directory: /home/YOURUSERNAME/harvestms/staticfiles

STEP 6 — Collect static files and go live
  Back in the Bash console:
       workon harvestms-env    (or: source harvestms-env/bin/activate)
       python manage.py collectstatic --noinput

  Go back to the "Web" tab and click the big green "Reload" button.
  Your system is now live at: https://YOURUSERNAME.pythonanywhere.com

----------------------------------------------------------
LOGIN
  Visit https://YOURUSERNAME.pythonanywhere.com/accounts/login/
  Use the superuser account you created in Step 4, or click "Sign up"
  to create a Farm Staff / Supervisor account.

SAMPLE DATA
  Run the Step 4.5 commands above to load it. It gives you a seeded
  "Maize" crop profile, a registered plot, 3 historical harvest records,
  and one AI prediction — so you can demonstrate the AI module
  (Stage 2: Statistical) immediately without entering data first.

NEED HELP?
  If any step produces an error, copy the exact error message back to
  Claude and it can be diagnosed and fixed.
