# What suncal can do for you 🌞❤️🌜
Would you like to know when the sun rises next week on Tue and have an entry in your calendar for this event without any 
manual effort and 100% for free? Then suncal is the right tool for you!

In general you can use this application to create Astronomical Calendars for a calendar application of your 
choice. For example you might want to keep track of the time of sunrise and sunset in your location for the whole 
year 2025. Or you are curious about the moon phases and would like to have entries in your calendar for every full
moon within the next two months. Currently we support the following event types:

- Sunrise
- Sunset
- Moonrise
- Moonset
- Moonphases (New moon, First Quarter, Full Moon, Last Quarter)
- Golden Hour in the morning and evening (center of sun between 4 degrees below and 6 degrees above the horizon)
- Blue Hour in the morning and evening (center of sun between 4 and 8 degrees below the horizon)

You can use this command line tool to either generate a 
[standard ics](https://datatracker.ietf.org/doc/html/rfc5545) file which you can then import into any calendar
application you like or you can have suncal create events in your Google calendar directly (via calls to the Google
calendar API) which requires advanced setup (as detailed below).

To create events you need to specify your geographic location (longitude & latitude) and a period of time (start and
end date). Suncal will determine the timezone of the events according to the location automatically. (You can override
this automatic timezone by providing your own.)

# Getting started
## Installation of suncal

The application was built with [poetry](https://python-poetry.org/) and depends on python 3.11, so make sure you have 
*poetry* and any minor version of python 3.11 installed on your system. The poetry version we tested with is 1.3.2. 

When poetry was installed successfully, clone this repository, cd to the repository and run

```bash
poetry install
```
This will set up a virtual environment and install the command line application (including all dev and non-dev dependencies).

You are now ready to create ics files according to your specifications.

## Create ics calendar files

You can see a description of all command line options by running:

```bash
poetry run suncal ics --help
```

### Example

Create a calendar ics file for every sunrise in the year 2025 for Berlin, Germany.

```bash
poetry run suncal ics --from 2025-1-1 --to 2025-12-31 --event sunrise --long 13.41 --lat 52.52 \ 
--filename sunrise-berlin-germany-2025.ics
```

The file name is an optional argument: if you don't provide a name, it will be generated from the name of the event and
the current timestamp. Most calendar apps let you choose a name for this particular calendar when you import the ics file. The calendar events will be created in the timezone of the provided location. If you want to override the 
timezone setting, you can provide a valid [tz timezone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) value to an additional command line argument called "timezone", e.g.

```bash
--timezone  Europe/Kyiv
```
The parsing of the timezone is case-insensitive, meaning you could also provide timezone string `europe/kyiv` or `Europe/kyiv` instead.

## Create astronomical calendars directly in your personal Google Calender 

Suncal also supports the direct insertion of the desired events in your personal Google Calendar (which circumvents
the previous creation of an ics calendar file). This requires a bit of an advanced setup as you need to have credentials and short-lived access tokens to communicate with the google calendar API. 

To obtain credentials, you first have to create a project in Google cloud with access to the Google Calendar API
enabled. Then in this project you can create credentials and download them. The downloaded json file will have some
rather lengthy cryptic name. Make sure to rename it to `credentials.json` and move it into the root directory
of this project (i.e. at the same level as this readme file). For more details on how to setup your Google cloud project correctly, please refer to these [python quickstart](https://developers.google.com/calendar/quickstart/python) guidelines. The first time you instruct suncal to create google calendar events, an authentication flow will start 
automatically and create/refresh access tokens for your credentials.

Navigate into the project folder (top level) and then run

```bash
poetry run suncal api --help
```

to see a description of all command line options for direct event insertion in your target Google calendar.

### Example

Create all sunrise calendar events in the year 2025 for Berlin, Germany and add them to a Google calendar named "Sonne".

```bash
poetry run suncal api --cal Sonne --from 2025-1-1 --to 2025-12-31 --event sunrise \
 --long 13.41 --lat 52.52
```

Note: You have to specify the name of your target calendar (`--cal Sonne` in the example above) **but** if a calendar 
with that name does not exist, it will be created for you automatically.

### Example II

Create a calendar for the moonphases for April 2025 in RedWood City, California and add them to a calendar named "moon".

```bash
poetry run suncal api --cal moon --from 2025-4-01 --to 2025-4-30 --event moonphase \ 
--long -122.2281 --lat 37.4848
```

# Rules for collaborators

This repo uses type annotations. To add code, create a new branch and make sure to run all checks before setting up your PR: cd to the repo, then run:

```bash
./qa/pychecks.sh
```

If any of the checks fail, the PR won't be accepted. If you add code, you also add tests.
"If you love it put a test on it." (source unknown)

# Main Dependencies

Our calculations of sun and moon events are based on [skyfield](https://rhodesmill.org/skyfield/).
We use [timezonefinder](https://github.com/jannikmi/timezonefinder) to determine the timezone from the GPS coordinates
provided by the user.

# Debugging
## Installation issues
1. We know that older poetry versions (1.1.3 and 1.1.4) do not correctly install the dev tool dependencies despite resolving them correctly. Make sure to use poetry 1.3.2 or try a higher version.
