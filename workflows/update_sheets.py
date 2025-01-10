import datetime
import logging
from zoneinfo import ZoneInfo

import pandas as pd
import pygsheets

from utils.data_config import DATA_CONFIGURATIONS


logger = logging.getLogger(__name__)


def _get_new_records(sheet_df: pd.DataFrame, api_df: pd.DataFrame, id_col: str) -> pd.DataFrame:
    ids_df = sheet_df[[id_col]].copy()
    result = pd.merge(
        api_df,
        ids_df,
        indicator=True,
        how="outer",
        on=[id_col]).query("_merge=='left_only'")
    return result.drop(["_merge"], axis=1)


def _update_existing_records(sheet_df: pd.DataFrame, api_df: pd.DataFrame, id_col: str) -> pd.DataFrame:
    """Generalized func to update one dataframe with data from another"""
    df = sheet_df.copy()
    df = df.set_index(id_col)
    current_data_df = api_df.set_index(id_col)
    df.update(current_data_df)
    df = df.reset_index()
    return df


def _update_timestamp(worksheet: pygsheets.Worksheet, timestamp_cell: str) -> None:
    timestamp = datetime.datetime.now(tz=ZoneInfo("America/Los_Angeles"))
    d_stamp = timestamp.strftime("%x")
    t_stamp = timestamp.strftime("%-I:%M %p")
    worksheet.update_value(timestamp_cell, f"LAST UPDATED: {d_stamp} @ {t_stamp}")


def update_google_sheet(data: pd.DataFrame, spreadsheet: pygsheets.Spreadsheet, data_config: str) -> None:
    config = DATA_CONFIGURATIONS[data_config]
    logger.info(f"Updating {config['sheet_name']} sheet")
    data = data.rename(config["field_mappings"], axis=1)
    data = data[config["field_filter_and_order"]]
    data.to_csv(f"{config['sheet_name']}.csv", index=False)

    worksheet = spreadsheet.worksheet_by_title(config["sheet_name"])
    sheet_df = worksheet.get_as_df(start="A2", include_tailing_empty=False)

    sheet_df = _update_existing_records(sheet_df, data, config["id_field"])
    new_records = _get_new_records(sheet_df, data, config["id_field"])
    if len(sheet_df) > 0:
        merged_df = pd.concat([sheet_df, new_records])
    else:
        merged_df = new_records
    worksheet.set_dataframe(merged_df, "A2", copy_head=True)

    timestamp_cell = config.get("timestamp_cell")
    if timestamp_cell is not None:
        _update_timestamp(worksheet, timestamp_cell)
