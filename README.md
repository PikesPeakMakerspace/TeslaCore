# TESLA Core

TESLA Core is a REST API and database designed to manage member equipment access via card scans at Pikes Peak Makerspace (and beyond?). It's intended to improve member safety while assisting with non-profit reporting needs.

Card scans are made possible with TESLA access nodes (more on that soon) with the API used by the TESLA web app (more on that soon too).

## About Pikes Peak Makerspace

Visit our website at: [pikespeakmakerspace.org](https://pikespeakmakerspace.org)

We are a membership based, non-profit organization, that provides equipment and classes to empower our makers, skilled or novice, to turn their passionate ideas into physical things. Whatever project you have in mind, you can make it here!

### Our Mission

Pikes Peak Makerspace is a community of cooperative hobbyists and early-stage entrepreneurs that empowers members to turn ideas into reality. We strive to provide access to tools and resources to confidently and safely design, develop, and make.

## API Documentation

Checkout the [OpenAPI documentation here](https://pikespeakmakerspace.github.io/TeslaCore/) for the Tesla Core API.

## Setup

In a linux terminal clone and enter the directory with the source code.

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

Install Node.js 18 or higher.

Install the required packages using the make target

```
make env
```

Copy secret.sh.example to secret.sh and customize the values for your environment.

```
cp secret.sh.example secret.sh
nano secret.sh
# Change the default to something else!
```

## Run Development Server and UI

Set system environment variables for the flask app and activate virtual environment.

```
source env.sh
```

Run the API server for local development

```
make dev
```

Start React for development

```
cd ui
npm run start
```

Wait for the browser to launch the UI.

## Run Production Server and UI

Set system environment variables for the flask app and activate virtual environment.

```
source env.sh
```

Build the React app to be delivered as static files by the API server.

```
make buildui
```

Run the production server.

```
make run
```

## Making Database Structure Changes

After making changes to database models (models.py), those changes will need to be reflected in the database. To do this, run the following command to generate a migration script :

```
flask db migrate -m "Add a useful description for the migration here."
```

Then after reviewing the migration file in `/migrations/versions` (need to review as it may not catch everything), run the following command to apply the migration to the database:

```
flask db upgrade
```

For more information on database migrations, see the [Flask-Migrate documentation](https://flask-migrate.readthedocs.io/en/latest/).

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

## Contribution Rules (work in progress)

edits to markdown can happen directly in main, all other changes happen in feature branches

```

```

## Database Migration Issue Resolution

I was running into a "multiple heads" issue while making lots of changes. Keep this in mind if you run into the same issue:
https://www.arundhaj.com/blog/multiple-head-revisions-present-error-flask-migrate.html
https://blog.jerrycodes.com/multiple-heads-in-alembic-migrations/
