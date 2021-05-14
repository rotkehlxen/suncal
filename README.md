# Purpose 🌞🌞🌞
Create google calendar with sunrise, sunset, golden hour etc. for specified
location and date(s). To learn about Google APIs, I want to insert events into my personal calendar using api calls.
However, for the common user, this is very cumbersome! You have to register this app in google cloud and obtain 
authentication tokens (see [here](https://developers.google.com/calendar/quickstart/python)) and potentially risk 
hitting the api quota for free use (I have no idea about the limits!).
Potentially useless note: It is also possible to send batch requests (put several API calls into a single HTTP request). 

To avoid all the above mentioned issues, the script should be able to create a .ics calendar file that can be 
imported using the google calendar web interface. 

# Rules for collaborators
If you add a function/class, you also add a corresponding test. This repo uses type annotation. To add code, 
create a new branch and make sure to run all checks before setting up your PR: cd to the repo, then run:

```bash
./qa/pychecks.sh
```
If any of the checks fail, the PR will not be accepted.

To run the application execute this line in terminal:
```bash
poetry run python path/to/capi-quickstart.py
```

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
