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
    ACCOUNTING_APP_FOLDER_NAME,
    PAYMENT_APP_EXPORT_FOLDER_NAME,
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

# def download_latest_sqlite_file(drive_service):
#     results = drive_service.files().list(
#         q="name contains 'MMAuto'",
#         fields="files(id, name, createdTime)",
#         orderBy="createdTime desc",
#         pageSize=1
#     ).execute()

#     files = results.get('files', [])
#     if not files:
#         logging.warning("No matching SQLite files found.")
#         return None

#     file = files[0]
#     request_drive = drive_service.files().get_media(fileId=file['id'])
#     fh = io.BytesIO()
#     downloader = MediaIoBaseDownload(fh, request_drive)

#     done = False
#     while not done:
#         status, done = downloader.next_chunk()
#         logging.info(f"Download progress: {int(status.progress() * 100)}%")

#     fh.seek(0)
#     # === Use NamedTemporaryFile ===
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mmbak") as temp_file:
#         temp_file.write(fh.read())
#         temp_file.flush()
#         temp_file_path = temp_file.name  # Save the path for use outside the block

#     logging.info(f"Downloaded file saved temporarily at '{temp_file_path}'.")
#     return temp_file_path
def download_latest_sqlite_file(drive_service):
    # Find the Accounting App folder
    folder_results = drive_service.files().list(
        q=(
            f"name = '{ACCOUNTING_APP_FOLDER_NAME}' "
            f"and mimeType = 'application/vnd.google-apps.folder' "
            f"and trashed = false"
        ),
        fields="files(id, name)",
        pageSize=1
    ).execute()

    folders = folder_results.get("files", [])

    if not folders:
        logging.warning(
            f"Drive folder '{ACCOUNTING_APP_FOLDER_NAME}' not found."
        )
        return None

    folder_id = folders[0]["id"]

    logging.info(
        f"Using Drive folder '{ACCOUNTING_APP_FOLDER_NAME}' "
        f"(ID: {folder_id})"
    )

    def get_latest_file(name_pattern):
        results = drive_service.files().list(
            q=(
                f"name contains '{name_pattern}' "
                f"and '{folder_id}' in parents "
                f"and trashed = false"
            ),
            fields="files(id, name, createdTime)",
            orderBy="createdTime desc",
            pageSize=1
        ).execute()

        files = results.get("files", [])
        return files[0] if files else None

    latest_mmauto = get_latest_file("MMAuto")
    latest_mmgf = get_latest_file("MMGF")

    if latest_mmgf and latest_mmauto:
        if latest_mmgf["createdTime"] >= latest_mmauto["createdTime"]:
            selected_file = latest_mmgf
        else:
            selected_file = latest_mmauto

    elif latest_mmgf:
        selected_file = latest_mmgf

    elif latest_mmauto:
        selected_file = latest_mmauto

    else:
        logging.warning(
            f"No MMAuto or MMGF files found in "
            f"'{ACCOUNTING_APP_FOLDER_NAME}'."
        )
        return None

    logging.info(
        f"Selected backup: {selected_file['name']} "
        f"(created: {selected_file['createdTime']})"
    )

    request = drive_service.files().get_media(
        fileId=selected_file["id"]
    )

    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        logging.info(
            f"Download progress: {int(status.progress() * 100)}%"
        )

    fh.seek(0)

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mmbak"
    ) as temp_file:
        temp_file.write(fh.read())
        temp_file.flush()
        temp_file_path = temp_file.name

    logging.info(
        f"Downloaded '{selected_file['name']}' "
        f"to '{temp_file_path}'."
    )

    return temp_file_path