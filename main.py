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

def create_date_range(days: int = 5) -> List[datetime.date]:
    return sorted([(datetime.datetime.now() - datetime.timedelta(days=i)).date() for i in range(days)])

def get_sleep_from_date_range(fb: fitbit.Fitbit, days: int = 5) -> pd.DataFrame:
    sleep_dataframes = []
    dates_to_get = create_date_range(days)
    for dt in dates_to_get:
        sleep_data = fb.get_sleep(dt)
        sleep(3)
        df = parse_sleep_data(sleep_data)
        sleep_dataframes.append(df)
    return pd.concat(sleep_dataframes)


def get_nutrition_data_from_date_range(fb: fitbit.Fitbit, days: int = 5) -> pd.DataFrame:
    data = []
    common_args = _get_common_api_args(fb)
    dates_to_get = create_date_range(days)
    for dt in dates_to_get:
        str_date = dt.strftime("%Y-%m-%d")
        base_url = "{0}/{1}/user/{2}/foods/log/date".format(*common_args)
        url = f"{base_url}/{str_date}.json"
        food = fb.make_request(url)
        logger.info(f"Getting nutrition data from {str_date}")
        sleep(3)
        _ = food.pop("foods", None)
        food["date"] = str_date
        data.append(food)
    return pd.json_normalize(data)


def parse_sleep_data(sleep_data: dict) -> pd.DataFrame:
    data = []
    slp = sleep_data["sleep"]
    for record in slp:
        record.pop("minuteData")
        data.append(record)
    return pd.DataFrame(data)


def connect_to_gsheet() -> pygsheets.Spreadsheet:
    client = pygsheets.authorize(service_account_file=GSHEET_CREDENTIALS)
    return client.open_by_key(GSHEET_ID)


def update_sheet(data: pd.DataFrame, spreadsheet: pygsheets.Spreadsheet, data_config: str) -> None:
    config = DATA_CONFIGURATIONS[data_config]
    data = data.rename(config["field_mappings"], axis=1)
    data = data[config["field_filter_and_order"]]
    data.to_csv(f"{config['sheet_name']}.csv", index=False)

    worksheet = spreadsheet.worksheet_by_title(config["sheet_name"])
    sheet_df = worksheet.get_as_df(start="A2", include_tailing_empty=False)

    sheet_df = _update_dataframe(sheet_df, data, config["id_field"])
    new_records = _get_new_records(sheet_df, data, config["id_field"])
    if len(sheet_df) > 0:
        merged_df = pd.concat([sheet_df, new_records])
    else:
        merged_df = new_records
    worksheet.set_dataframe(merged_df, "A2", copy_head=True)

    timestamp_cell = config.get("timestamp_cell")
    if timestamp_cell is not None:
        _update_timestamp(worksheet, timestamp_cell)


def _update_dataframe(sheet_df: pd.DataFrame, api_df: pd.DataFrame, id_col: str) -> pd.DataFrame:
    """Generalized func to update one dataframe with data from another"""
    df = sheet_df.copy()
    df = df.set_index(id_col)
    current_data_df = api_df.set_index(id_col)
    df.update(current_data_df)
    df = df.reset_index()
    return df


def _get_new_records(sheet_df: pd.DataFrame, api_df: pd.DataFrame, id_col: str) -> pd.DataFrame:
    ids_df = sheet_df[[id_col]].copy()
    result = pd.merge(
        api_df,
        ids_df,
        indicator=True,
        how="outer",
        on=[id_col]).query("_merge=='left_only'")
    return result.drop(["_merge"], axis=1)

def _update_timestamp(worksheet: pygsheets.Worksheet, timestamp_cell: str) -> None:
    timestamp = datetime.datetime.now(tz=ZoneInfo("America/Los_Angeles"))
    d_stamp = timestamp.strftime("%x")
    t_stamp = timestamp.strftime("%-I:%M %p")
    worksheet.update_value(timestamp_cell, f"LAST UPDATED: {d_stamp} @ {t_stamp}")


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

    df = get_nutrition_data_from_date_range(fb)
    df = df.fillna("-")
    spreadsheet = connect_to_gsheet()

    logger.info("Updating Sheet")
    update_sheet(df, spreadsheet, "NUTRITION")

    logger.info("Refreshing tokens")
    fb.client.refresh_token()


if __name__ == "__main__":
    main()
