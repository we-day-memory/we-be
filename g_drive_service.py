import json
import os
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials

class GoogleDriveService:
    def __init__(self):
        self._SCOPES=['https://www.googleapis.com/auth/drive']

        # _base_path = os.path.dirname(__file__)
        # _credential_path=os.path.join(_base_path, 'credentials.json')
        # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = _credential_path

    def build(self):
        # Load credentials from environment variable
        credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON_DD")
        if not credentials_json:
            raise ValueError("Environment variable GOOGLE_APPLICATION_CREDENTIALS_JSON is not set.")
 
        # Parse JSON credentials
        credentials_info = json.loads(credentials_json)

        # Create credentials object
        creds = Credentials.from_service_account_info(credentials_info, scopes=self._SCOPES)

        # Build the Drive service
        service = build('drive', 'v3', credentials=creds)

        return service
