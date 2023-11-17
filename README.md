# TESLA Core

This is a small project being used to prototype a Python REST API for a larger volunteer project. I haven't used Python all that much, especially in a web server scenario. Let's fix that here.

## Setup
in a linux terminal clone and enter the directory with the source code
```
cd TeslaCore
```

Install Python (if not already installed)

```
sudo apt install python3-pip
```

Install `venv`, a Python virtual environment to keep things clean and separate from system-installed Python. On Ubuntu:

```
apt install python3.10-venv
```

Install the required packages using the make target
```
make env
```

Setup the secrets (such as `TESLA_JWT_SECRET_KEY`) and place in the file `secrets.sh`
Set system environment variables for the flask app and activate virtual environment
```
source env.sh
```

Run the app using the make target
```
make run
```

## Repeated Setup
Source the environment
```
source env.sh
```

Run the app
```
make run
```


## Random Notes

TODO: Figure this out for the app and document it here:

```
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
```

werkzeug==2.3.0 was installed as a url_decode function in flask was deprecated, latest version not available just yet. Consider updating when possible and/or dig further on this.

All about JWTs:
https://flask-jwt-extended.readthedocs.io/_/downloads/en/stable/pdf/

Database migration how-to with hints about referencing environment variables:
https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database

Nice tool if wanting to make edits to db directly:
https://sqlitebrowser.org

Nice REST API guidelines:
https://medium.com/paperplanetechworks/api-architecture-11-design-best-practices-for-rest-apis-d26a35be603c

User role needs/protection for endpoints:
https://pythonhosted.org/Flask-Principal/

## Contribution Rules
edits to markdown can happen directly in main, all other changes happen in feature branches
