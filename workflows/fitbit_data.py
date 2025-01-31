import datetime
import logging
from http.client import responses
from time import sleep
from typing import List, Union, Tuple

import fitbit
import pandas as pd


logger = logging.getLogger(__name__)

def _create_common_api_args(fb: fitbit.Fitbit, user_id=None):
    common_args = (fb.API_ENDPOINT, fb.API_VERSION,)
    if not user_id:
        user_id = '-'
    common_args += (user_id,)
    return common_args


def _create_date_range(days: int = 5) -> List[datetime.date]:
    if days > 31:
        logger.info(f"Changing days to 31. {days} is too many.")
        days = 31
    return sorted([(datetime.datetime.now() - datetime.timedelta(days=i)).date() for i in range(days)])


def fetch_activity(fb: fitbit.Fitbit, days: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    activity_log_data = []
    activity_summary_data = []
    common_args = _create_common_api_args(fb)
    dates_to_get = _create_date_range(days)
    for dt in dates_to_get:
        str_date = dt.strftime("%Y-%m-%d")
        base_url = "{0}/{1}/user/{2}/activities/date".format(*common_args)
        url = f"{base_url}/{str_date}.json"
        activity = fb.make_request(url)
        logger.info(f"Getting Activity data from {str_date}")
        log_data = _parse_activity_log(activity["activities"])
        if log_data is not None:
            activity_log_data.extend(log_data)
        summary_data = _parse_activity_summary(activity["summary"], str_date)
        activity_summary_data.append(summary_data)
        sleep(3)
    summary_df = pd.json_normalize(activity_summary_data)
    log_df = pd.json_normalize(activity_log_data)
    return summary_df, log_df


def _parse_activity_log(data: List[dict]) -> Union[None, list]:
    if data:
        return data
    else:
        return None


def _parse_activity_summary(data: dict, summary_date: str) -> dict:
    _ = data.pop("distances")
    data["date"] = summary_date
    return data


def fetch_nutrition(fb: fitbit.Fitbit, days: int) -> pd.DataFrame:
    data = []
    common_args = _create_common_api_args(fb)
    dates_to_get = _create_date_range(days)
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


def fetch_sleep_logs(fb: fitbit.Fitbit, days: int) -> pd.DataFrame:
    sleep_dataframes = []
    dates_to_get = _create_date_range(days)
    for dt in dates_to_get:
        sleep_data = fb.get_sleep(dt)
        sleep(3)
        df = _parse_sleep_data(sleep_data)
        sleep_dataframes.append(df)
    df = pd.concat(sleep_dataframes)
    return df


def _parse_sleep_data(sleep_data: dict) -> pd.DataFrame:
    data = []
    slp = sleep_data["sleep"]
    summary = sleep_data["summary"]
    stages = summary.get("stages")
    if stages is not None:
        stages = summary.pop("stages")
    else:
        stages = {
            "deep": "0",
            "light": "0",
            "rem": "0",
            "wake": "0"
        }
    summary = summary | stages
    for record in slp:
        record.pop("minuteData")
        record = record | summary
        data.append(record)
    return pd.DataFrame(data)


def fetch_weight_logs(fb: fitbit.Fitbit, days: int) -> pd.DataFrame:
    common_args = _create_common_api_args(fb)
    dates_to_get = _create_date_range(days)
    start_date = dates_to_get[0].strftime("%Y-%m-%d")
    end_date = dates_to_get[-1].strftime("%Y-%m-%d")
    base_url = "{0}/{1}/user/{2}/body/log/weight/date".format(*common_args)
    url = f"{base_url}/{start_date}/{end_date}.json"
    logger.info(f"Getting weight logs from {start_date} to {end_date}")
    response = fb.make_request(url)
    return pd.json_normalize(response["weight"])

