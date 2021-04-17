# from __future__ import print_function
# import datetime
# import pickle
# import os.path
# from googleapiclient.discovery import build
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
#
# # If modifying these scopes, delete the file token.pickle.
# SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
#
#
# def main():
#     """Shows basic usage of the Google Calendar API.
#     Prints the start and name of the next 10 events on the user's calendar.
#     """
#     creds = None
#     # The file token.pickle stores the user's access and refresh tokens, and is
#     # created automatically when the authorization flow completes for the first
#     # time.
#     if os.path.exists('token.pickle'):
#         with open('token.pickle', 'rb') as token:
#             creds = pickle.load(token)
#     # If there are no (valid) credentials available, let the user log in.
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             print("define flow")
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'credentials.json', SCOPES)
#             print("run local server")
#             creds = flow.run_local_server(port=0)
#         # Save the credentials for the next run
#         print("save token")
#         with open('token.pickle', 'wb') as token:
#             pickle.dump(creds, token)
#
#     print("build service")
#     service = build('calendar', 'v3', credentials=creds)
#
#     # Call the Calendar API
#     now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
#     print('Getting the upcoming 10 events')
#     events_result = service.events().list(calendarId='primary', timeMin=now,
#                                         maxResults=10, singleEvents=True,
#                                         orderBy='startTime').execute()
#     events = events_result.get('items', [])
#
#     if not events:
#         print('No upcoming events found.')
#     for event in events:
#         start = event['start'].get('dateTime', event['start'].get('date'))
#         print(start, event['summary'])
#
#
# if __name__ == '__main__':
#     main()
# try to create a google calendar event by calling the API
# what is the correct format of the payload?
import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# read and write access to google calendars AND calendar events:
# TODO: this scope is a bit too extensive - check how to be more specific
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]

creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists("token.pickle"):
    with open("token.pickle", "rb") as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        print("define flow")
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        print("run local server")
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    print("save token")
    with open("token.pickle", "wb") as token:
        pickle.dump(creds, token)

print("build service")
service = build("calendar", "v3", credentials=creds)


# create an event: I am not sure that None will be accepted
# it is ok for this dict to contain None values!!
# it is NOT ok for this dict to contain datetime objects

event = {
    "start": {"date": None, "dateTime": "2021-02-28T16:30:00+01:00", "timeZone": None},
    "end": {"date": None, "dateTime": "2021-03-01T16:30:00+01:00", "timeZone": None},
    "summary": "fake event",
}

event = service.events().insert(calendarId="primary", body=event).execute()
print("Event created: %s" % (event.get("htmlLink")))

# TODO: I think we have to close the service when we are done!!! (best use a context manager)
