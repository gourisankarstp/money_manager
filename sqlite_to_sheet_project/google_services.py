import os

import google.auth
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import logging
import tempfile
from sqlite_to_sheet_project.config import (
    MOUNTED_SERVICE_ACCOUNT_FILE,
    LOCAL_SERVICE_ACCOUNT_FILE,
    SCOPES,
    SERVICE_ACCOUNT_FILE,
)

def get_drive_and_creds():
    credential_file = SERVICE_ACCOUNT_FILE
    if credential_file is None and os.path.isfile(MOUNTED_SERVICE_ACCOUNT_FILE):
        credential_file = MOUNTED_SERVICE_ACCOUNT_FILE
    if credential_file is None and os.path.isfile(LOCAL_SERVICE_ACCOUNT_FILE):
        credential_file = LOCAL_SERVICE_ACCOUNT_FILE

    if credential_file:
        creds = Credentials.from_service_account_file(credential_file, scopes=SCOPES)
    else:
        # Uses the Cloud Run service account in production and the local ADC
        # configured by `gcloud auth application-default login` during development.
        creds, _ = google.auth.default(scopes=SCOPES)

    drive_service = build('drive', 'v3', credentials=creds, cache_discovery=False)

    return creds, drive_service

def download_latest_sqlite_file(drive_service):
    results = drive_service.files().list(
        q="name contains 'MMAuto'",
        fields="files(id, name, createdTime)",
        orderBy="createdTime desc",
        pageSize=1
    ).execute()

    files = results.get('files', [])
    if not files:
        logging.warning("No matching SQLite files found.")
        return None

    file = files[0]
    request_drive = drive_service.files().get_media(fileId=file['id'])
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request_drive)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        logging.info(f"Download progress: {int(status.progress() * 100)}%")

    fh.seek(0)
    # === Use NamedTemporaryFile ===
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mmbak") as temp_file:
        temp_file.write(fh.read())
        temp_file.flush()
        temp_file_path = temp_file.name  # Save the path for use outside the block

    logging.info(f"Downloaded file saved temporarily at '{temp_file_path}'.")
    return temp_file_path
