# What does suncal do? 🌞🌞🌞

Suncal creates a sun calendar. You can choose between the following events: sunrise, sunset, golden-hour-morning and
golden-hour-evening - which should be of particular interest for photographers 📷.
Parameters like geographic location (longitude & latitude), timezone and the range of dates for which these events 
should be created can be specified ad libitum. If you register this application in google cloud and grant read and write
access to your personal google calendar, the events can be inserted directly into your google calendar using api calls.
You specify the name of your target calendar and if it does not exist, it will be created for you.

Alternatively you can use this application to create an ics file and import it to any calendar you like. In that case,
registration/authentication are unnecessary.  

While the api functionality is only of interest for users of google calendar, the generated calendar ics file is 
universal (conforms to this [standard](https://datatracker.ietf.org/doc/html/rfc5545#page-102)) and so it can be 
imported to every calendar application. (it contains two (optional) fields that are only understood by google 
calendars but these are simply ignored by other calendar apps.) 
 
# How to run suncal

The application was built with [poetry](https://python-poetry.org/) and depends on python 3.7, so make sure you have 
poetry and any minor version of python 3.7 installed on your system (to manage several installations of python we recommend 
using [pyenv](https://github.com/pyenv/pyenv)). 

Clone this repository, cd to the repository and run

```bash
poetry install
```
This will set up a virtual environment and install the application (including all dev and non-dev dependencies).

## Use google calendar api to create calendar events

To allow insertion of events into your google calendar, the app has to be registered in google cloud and access to the
api enabled. The google cloud console is also the place where you can create credentials (a file named "credentials.json").
When you run the application for the first time, the authentication flow will lead to the creation of access tokens (the
credentials are required in this process!). All details of the process are outlined 
[here](https://developers.google.com/calendar/quickstart/python). 

Navigate into the project folder (top level) (credentials and access tokens must be stored in this directory as well),
then run

```bash
poetry run suncal api --help
```

to see a description of all command line options.
Example for a complete set of options:

```bash
poetry run suncal api --cal Sonne --from 2021-6-10 --to 2021-6-10 --event sunrise --timezone 'Europe/Berlin' \
--long 14.32 --lat 52
```

## Export events to ics file

If you want to export the sun calendar to an ics file, registration of this app in google cloud is unnecessary.
You can provide a name for the ics file, but if you don't, the name will be created automatically. You can see a
description of all command line options with:

```bash
poetry run suncal ics --help
```

Example:

```bash
poetry run suncal ics --from 2021-6-10 --to 2021-6-10 --event sunrise \
--long 14.32 --lat 52 --filename myIcsFile.ics
```

# Rules for collaborators

This repo uses type annotation. To add code, 
create a new branch and make sure to run all checks before setting up your PR: cd to the repo, then run:

```bash
./qa/pychecks.sh
```

If any of the checks fail, the PR will not be accepted. If you add a function/class, 
you also add a corresponding test.

# Dependencies

## astral
This package calculates various sun and moon parameters for specified
locations and dates. It has an inbuilt database that contains longitude,
latitude and timezones for the big cities in the world.

## google-api-python-client, google-auth-httplib2, google-auth-oauthlib
Tools for communication with google api and authentication flow.

## pydantic
Data validation and settings management using python type annotations.
Pydantic enforces type hints at runtime. Ideal for exchanging data with APIs.

## Dev dependencies
For a comprehensive list check the pyproject.toml.
