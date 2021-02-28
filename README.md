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
list, write your name next to it, so we don't do things several times.

## Specifications

### UI

Intended as a simple command line tool. Use e.g. [click](https://click.palletsprojects.com/en/7.x/) to create a 
standalone command line tool and use its functionality to parse command line parameters, check their validity and 
autogenerate documentation (or another tool if there is sth. even fancier out there.)

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

#### CLI
Set up the cli using click or some other tool.

#### astral wrapper
Write a function that returns start and end datetime of a given event ("sunrise", "sunset" or "goldenhour"). 
For sunrise and sunset, start and end are identical (but astral returns just one timestamp).

#### date ranges
Write a function that creates a list of dates between "from" and "to". E.g. if from="2021-02-01" and to="2021-02-03",
return list ["2021-02-01", "2021-02-02", "2021-02-03"]. Of course using python date type, not strings!

#### ics support
Implement mapping from list of GoogleCalEvents to ics file. 

#### event styles
Function that returns the event title string provided a type of event and the datetime object. Using the event styles 
shown above.

#### authentication flow
Function for authentication flow. Creates a token if it does not exit yet. The file suncal/capi-quickstart.py in this 
repo serves as an orientation! The SCOPE has to be changed to 'https://www.googleapis.com/auth/calendar' to obtain read
and write permissions for calendars and 'https://www.googleapis.com/auth/calendar.events' for read/write access to 
calendar events (see [here](https://developers.google.com/calendar/auth)).

#### main function (controlled by CLI)
Loop over all requested dates, then over all requested events. Calculate start and end time using the astral wrapper. 
Create GoogleCalEvent. Either serialize these events for the API, or export to ics. If we use the API, initialise the 
authentication flow (suncal/capi-quickstart serves as an orientation). Create service object for all API calls. Check if
the target calendar exits - if not, create it. Send all events to calendar. Done. 

# Dependencies

## astral
This package calculates various sun and moon parameters for specified
locations and dates. It has an inbuilt database that contains longitude,
latitude and timezones for the big cities in the world.

## google-api-python-client, google-auth-httplib2, google-auth-oauthlib

