import os
import io
import logging
import tempfile

import google.auth
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

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

    if credential_file is None and os.path.isfile(
        MOUNTED_SERVICE_ACCOUNT_FILE
    ):
        credential_file = MOUNTED_SERVICE_ACCOUNT_FILE

    if credential_file is None and os.path.isfile(
        LOCAL_SERVICE_ACCOUNT_FILE
    ):
        credential_file = LOCAL_SERVICE_ACCOUNT_FILE

    if credential_file:
        creds = Credentials.from_service_account_file(
            credential_file,
            scopes=SCOPES
        )
    else:
        # Uses the Cloud Run service account in production and the
        # local ADC configured by gcloud auth application-default login.
        creds, _ = google.auth.default(scopes=SCOPES)

    drive_service = build(
        "drive",
        "v3",
        credentials=creds,
        cache_discovery=False
    )

    return creds, drive_service


def get_drive_folder_id(
    drive_service,
    folder_name,
    parent_folder_id=None,
):
    query_parts = [
        f"name = '{folder_name}'",
        "mimeType = 'application/vnd.google-apps.folder'",
        "trashed = false",
    ]

    if parent_folder_id:
        query_parts.append(
            f"'{parent_folder_id}' in parents"
        )

    query = " and ".join(query_parts)

    logging.info(
        f"Searching Drive folder: '{folder_name}'"
    )
    logging.info(
        f"Drive query: {query}"
    )

    results = drive_service.files().list(
        q=query,
        fields="files(id, name, parents, mimeType)",
        pageSize=100,
        spaces="drive",
    ).execute()

    folders = results.get("files", [])

    logging.info(
        f"Found {len(folders)} matching folder(s) "
        f"for '{folder_name}'."
    )

    for folder in folders:
        logging.info(
            f"Folder found: {folder['name']} "
            f"(ID: {folder['id']})"
        )

    if not folders:
        logging.warning(
            f"Drive folder '{folder_name}' not found."
        )
        return None

    return folders[0]["id"]

def get_latest_file_from_folder(
    drive_service,
    folder_id,
    name_pattern=None,
    mime_type=None
):
    query_parts = [
        f"'{folder_id}' in parents",
        "trashed = false"
    ]

    if name_pattern:
        query_parts.append(
            f"name contains '{name_pattern}'"
        )

    if mime_type:
        query_parts.append(
            f"mimeType = '{mime_type}'"
        )

    results = drive_service.files().list(
        q=" and ".join(query_parts),
        fields="files(id, name, createdTime, mimeType)",
        orderBy="createdTime desc",
        pageSize=1
    ).execute()

    files = results.get("files", [])

    return files[0] if files else None


def download_file(drive_service, selected_file, suffix):
    logging.info(
        f"Selected file: {selected_file['name']} "
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

        if status:
            logging.info(
                f"Download progress: "
                f"{int(status.progress() * 100)}%"
            )

    fh.seek(0)

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp_file:
        temp_file.write(fh.read())
        temp_file.flush()
        temp_file_path = temp_file.name

    logging.info(
        f"Downloaded '{selected_file['name']}' "
        f"to '{temp_file_path}'."
    )

    return temp_file_path


def download_latest_sqlite_file(drive_service):
    folder_id = get_drive_folder_id(
        drive_service,
        ACCOUNTING_APP_FOLDER_NAME
    )

    if not folder_id:
        return None

    selected_file = None

    for name_pattern in ["MMAuto", "MMGF"]:
        file = get_latest_file_from_folder(
            drive_service,
            folder_id,
            name_pattern=name_pattern
        )

        if file:
            if (
                selected_file is None
                or file["createdTime"] > selected_file["createdTime"]
            ):
                selected_file = file

    if not selected_file:
        logging.warning(
            f"No MMAuto or MMGF files found in "
            f"'{ACCOUNTING_APP_FOLDER_NAME}'."
        )
        return None

    return download_file(
        drive_service,
        selected_file,
        suffix=".mmbak"
    )

def download_latest_paytm_export(drive_service):
    folder_id = get_drive_folder_id(
        drive_service,
        PAYMENT_APP_EXPORT_FOLDER_NAME
    )

    if not folder_id:
        return None

    selected_file = get_latest_file_from_folder(
        drive_service,
        folder_id,
        name_pattern="Paytm",
        mime_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    if not selected_file:
        logging.warning(
            f"No Paytm Excel files found in "
            f"'{PAYMENT_APP_EXPORT_FOLDER_NAME}'."
        )
        return None

    return download_file(
        drive_service,
        selected_file,
        suffix=".xlsx"
    )  