import json
import os
from time import sleep

import fitbit
import pandas as pd
import pygsheets

from utils.logger_config import get_logger
from utils.runtime_args import parse_runtime_args
from workflows import fitbit_data
from workflows.update_sheets import update_google_sheet

OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URL = os.getenv("REDIRECT_URL")
AUTH_URI = os.getenv("AUTH_URI")
REFRESH_URI = os.getenv("REFRESH_URI")
GSHEET_CREDENTIALS = os.getenv("GSHEET_CREDENTIALS")
GSHEET_ID = os.getenv("SHEET_ID")
TOKEN_FILE = os.getenv("TOKEN_FILE")


logger = get_logger()


def _get_tokens() -> dict:
    with open(TOKEN_FILE, "r") as file:
        return json.load(file)


def connect_to_gsheet() -> pygsheets.Spreadsheet:
    client = pygsheets.authorize(service_account_file=GSHEET_CREDENTIALS)
    return client.open_by_key(GSHEET_ID)


def _update_fitbit_tokens(tokens) -> None:
    new_access_token = tokens["access_token"]
    new_refresh_token = tokens["refresh_token"]
    updated_tokens = {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token
    }
    with open(TOKEN_FILE, "w") as file:
        json.dump(updated_tokens, file, indent=4)


def _get_common_api_args(fb: fitbit.Fitbit, user_id=None):
    common_args = (fb.API_ENDPOINT, fb.API_VERSION,)
    if not user_id:
        user_id = '-'
    common_args += (user_id,)
    return common_args


def main():
    tokens = _get_tokens()
    fb = fitbit.Fitbit(
        OAUTH_CLIENT_ID,
        CLIENT_SECRET,
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        refresh_cb=_update_fitbit_tokens
    )

    args = parse_runtime_args()

    days = args.days

    spreadsheet = connect_to_gsheet()

    if args.activity:
        summary_df, log_df = fitbit_data.fetch_activity(fb, days=days)
        update_google_sheet(summary_df, spreadsheet, "ACTIVITY_SUMMARY")
        update_google_sheet(log_df, spreadsheet, "ACTIVITY_LOGS")

    if args.nutrition:
        df = fitbit_data.fetch_nutrition(fb, days=days)
        df = df.fillna("-")
        update_google_sheet(df, spreadsheet, "NUTRITION")

    if args.sleep:
        df = fitbit_data.fetch_sleep_logs(fb, days=days)
        df = df.fillna("-")
        update_google_sheet(df, spreadsheet, "SLEEP")

    if args.weight:
        df = fitbit_data.fetch_weight_logs(fb, days=days)
        if len(df) > 0:
            update_google_sheet(df, spreadsheet, "WEIGHT")
        else:
            logger.info("No data to update for weight")

    if args.refresh_token:
        logger.info("Refreshing tokens")
        fb.client.refresh_token()


if __name__ == "__main__":
    main()
