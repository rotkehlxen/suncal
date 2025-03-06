import os
import pickle
import sys
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


def get_credentials(scopes: List[str]) -> Credentials:
    """
    Create or refresh access tokens for the credentials provided in the credentials.json file.
    """

    # check that credentials.json is available
    if not os.path.exists('credentials.json'):
        sys.exit(
            "File 'credentials.json' is missing! Make sure the file is located in the suncal project folder (in the "
            "same folder as README.md). If you have no credentials file, you need to create a project "
            "in google cloud console, grant the project access to the google calendar api and create "
            "credentials for your google account. For more information check out "
            "https://developers.google.com/workspace/guides/create-credentials"
        )

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
            print("define authentication flow")
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", scopes
            )
            print("run local server")
            flow.run_local_server(port=0)
            creds = flow.credentials
        # Save the credentials for the next run
        print("save token")
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return creds
