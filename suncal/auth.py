import os
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


def get_credentials(scopes: list[str]) -> Credentials:

    # check that credentials.json is available
    if not os.path.exists('credentials.json'):
        sys.exit(
            "File 'credentials.json' is missing! Make sure the file is located in the suncal project folder (in the "
            "same folder as README.md). If you have no credentials file, you have to register this application "
            "in google cloud console, grant this application access to the google calendar api and create "
            "credentials for your google account. For more information check out "
            "https://developers.google.com/workspace/guides/create-credentials"
        )

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print('refreshing your token')
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", scopes
            )
            print("run local server")
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        print("save token")
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds
