import os
import pickle
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


def get_credentials(scopes: List[str]) -> Credentials:
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
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", scopes
            )
            print("run local server")
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        print("save token")
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return creds
