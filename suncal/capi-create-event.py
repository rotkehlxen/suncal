# try to create a google calendar event by calling the API
# what is the correct format of the payload?
import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# read and write access to google calendars AND calendar events
SCOPES = ['https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/calendar.events']

creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        print("define flow")
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        print("run local server")
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    print("save token")
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

print("build service")
service = build('calendar', 'v3', credentials=creds)


# create an event
event = {
  'summary': 'fake event',
  'start': {
    'dateTime': '2015-05-28T09:00:00-07:00',
    'timeZone': 'America/Los_Angeles',
  },
  'end': {
    'dateTime': '2015-05-28T17:00:00-07:00',
    'timeZone': 'America/Los_Angeles',
  },
}

