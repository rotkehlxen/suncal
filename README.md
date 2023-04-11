- [What suncal can do for you](https://github.com/rotkehlxen/suncal#what-suncal-can-do-for-you-%EF%B8%8F)
  - [Supported Events](https://github.com/rotkehlxen/suncal#supported-events)
- [Install and run Suncal](https://github.com/rotkehlxen/suncal#install-and-run-suncal)
  - [Export events to Google Calendar](https://github.com/rotkehlxen/suncal#use-google-calendar-api-to-create-calendar-events)
  - [Export events to ics file](https://github.com/rotkehlxen/suncal#export-events-to-an-ics-file)
- [Rules for collaborators](https://github.com/rotkehlxen/suncal#rules-for-collaborators)


# What suncal can do for you 🌞❤️🌜
Would you like to know when the sun rises next week on Tue and have an entry in your calendar for this event without any 
manual effort and 100% for free? Then suncal is the right tool for you!

You can use this command line tool to either generate a 
[standard ics](https://datatracker.ietf.org/doc/html/rfc5545#page-102) file which you can import into any calendar
application you like or you can have suncal create events in your Google calendar directly (via calls to the Google
calendar API).

To create these events you need to specify the geographic location (longitude & latitude) and a range of dates. 
Suncal will determine the timezone of the location automatically.

## Supported Events

### 1 Sunrise and Sunset
### 2 Golden Hour and Blue Hour

The Golden Hour is a period of time around sunrise/sunset, i.e. where the center of the sun is between -4 and 6 degrees 
above the horizon. The Blue Hour is a period before sunrise/after sunset where the natural light is infused by a lot of 
blue tones. We define it as the period in which the center of the sun is between 8 and 4 degrees below the horizon. 
The Golden/Blue Hour actually varies a lot in length depending on location. You can create the corresponding calendar 
events by using the event names 'golden_hour_morning', 'golden_hour_evening', 'blue_hour_morning' or 'blue_hour_evening'. 

### 3 Moonrise and Moonset
### 4 The Moon Phases

|     phase     | symbol in calendar |
|:-------------:|:------------------:|
|   New moon    |         🌚         |
| First Quarter |         🌓         |
|   Full Moon   |         🌝         |
| Last Quarter  |         🌗         |

We are using standard symbols for those phases, although we are aware that the partially lit moon appears 
differently across the latitudes. Suncal creates an all-day event for each phase but the event description contains the 
precise time at which this phase can be observed.

# Install and run Suncal

The application was built with [poetry](https://python-poetry.org/) and depends on python 3.11.2, so make sure you have 
*poetry* and any minor version of python 3.11 installed on your system. The package will probably work with any python 
version 3.9 and above but we are only testing in 3.11. The poetry version we tested with is 1.3.2, and we know that 
older versions (1.1.3 and 1.1.4) do not correctly install the dev tool dependencies despite resolving them correctly. 

Clone this repository, cd to the repository and run

```bash
poetry install
```
This will set up a virtual environment and install the command line application 
(including all dev and non-dev dependencies).

## Use Google Calendar api to create calendar events

To allow insertion of events into your Google Calendar, the app has to be registered in Google Cloud and access to the
api enabled. The Google Cloud console is also the place where you can create credentials (a file named "credentials.json").
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
poetry run suncal api --cal Sonne --from 2023-6-10 --to 2023-6-10 --event sunrise \
 --long 14.32 --lat 52
```
The command above will create only one event in a Google Calendar named "Sonne" - for the sunrise on 6.10.2023 in 
Berlin/Germany.

Note: you have to specify the name of your target calendar (`--cal Sonne` in the example above) **but** if a calendar 
with that name does not exist, it will be created for you automatically.

Another example for Redwood City in California:

```bash
poetry run suncal api --cal Sonnenaufgang --from 2023-1-01 --to 2023-12-31 --event sunrise \ 
--long -122.2281 --lat 37.4848
```
The command above creates sunrise events for the whole year 2023.

## Export events to an ics file

If you want to export the sun calendar to an ics file, registration of this app in Google Cloud is unnecessary.
You can provide a name for the ics file, but if you don't, the name will be created automatically. You can see a
description of all command line options with:

```bash
poetry run suncal ics --help
```

Example:

```bash
poetry run suncal ics --from 2021-6-10 --to 2021-6-10 --event sunrise --long 14.32 --lat 52 \ 
--filename myIcsFile.ics
```

The file name is an optional argument: if you don't provide a name, it will be generated from the name of the event and
the current timestamp. 

# Rules for collaborators

This repo uses type annotation. To add code, 
create a new branch and make sure to run all checks before setting up your PR: cd to the repo, then run:

```bash
./qa/pychecks.sh
```

If any of the checks fail, the PR will not be accepted. If you add a function/class, you also add a corresponding test.

# Main Dependencies

## skyfield
Our calculations of sun and moon events are based on [skyfield](https://rhodesmill.org/skyfield/).

## google-api-python-client, google-auth-oauthlib, google
Tools for communication with the Google API and authentication flow.

## timezonefinder
We use [timezonefinder](https://github.com/jannikmi/timezonefinder) to determine the timezone from the GPS coordinates
provided by the user.
