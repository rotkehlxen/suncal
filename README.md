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
If you add a function/class, you also add a corresponding test. If you want to work on one of the items in the todo
list, write your name next to it, so we don't do things several times. This repo uses type annotation. Before you 
commit your code, sort the imports with **isort**, reformat the code with **black** and check that typing is correct using 
**mypy**. cd to the project folder and run:

```bash
poetry run isort .
poetry run black .
poetry run mypy .
```

The script suncal/capi-quickstart.py illustrates how to create an event in your primary calendar, how to create a new 
calendar and how to list the summary (i.e. the names) of all the calendars that are associated with your account (
comment out specific sections as needed). After registering capi-quickstart.py in google cloud, you can run the script
with:

```bash
poetry run python path/to/capi-quickstart.py
```
Credentials will be created and saved (as pickle) if they do not exist. (Do not forget to install the suncal package
beforehand.)

## Specifications

### UI

Intended as a simple command line tool. Use [typer](https://typer.tiangolo.com/) to create a 
standalone command line tool and use its functionality to parse command line parameters, check their validity and 
autogenerate documentation.

#### CLI parameters

The following parameters are useful for the dev phase and can be changed for productive runs. For example, 
I might want to create this calendar for a year or two and it would be cumbersome to supply a "from" and "to"
date for this. 

|   parameter  | specs |
|--------------|-------|
| calendar id  | id of target google calendar. Create if it does not exist. |
| from         | "yyyy-mm-dd" from this day ... (default today) |
| to           | "yyyy-mm-dd" to this day ... (default today + 1 week) |
| event        | e.g. "sunrise", for the first draft restrict to choices {"sunrise", "sunset", "goldenhour"} |
| timezone     | e.g. "Europe/Berlin" IANA timezone string (default Berlin) |
| longitude    | e.g. -122.236355 for Redwood City CA (default Berlin) |
| latitude     | e.g 37.485215 for Redwood City CA (default Berlin) |
| return       | "api" (create events by api call) or "ics" (export ics calendar file) | 

### Calendar event style

#### Sunrise

↑🌞 6:05 am

#### Sunset

↓🌞 7:10 pm

#### Golden hour
📷 golden hour

### TO DO
Some of the following todos can surely be split into several tasks (and can result in multiple functions/classes).

#### CLI: Thomas
Set up the CLI using **typer**.

#### ics support
Implement mapping from list of GoogleCalEvents to ics file. 

#### main function (controlled by CLI): Franzi
Loop over all requested dates, then over all requested events. Calculate start and end time using the astral wrapper. 
Create GoogleCalEvent. Either serialize these events for the API, or export to ics. If we use the API, initialise the 
authentication flow. Check if the target calendar exits - if not, create it. Send all events to calendar. Done. 

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
