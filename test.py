from datetime import date
import json

import pandas
import pygsheets

from FitBitAPI import api
from FitBitAPI.exceptions import HTTPUnauthorized
import pprint


access_token = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyMzhINVIiLCJzdWIiOiIyWEpWNlEiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJzZXQgcm94eSBycHJvIHJudXQgcnNsZSByYWN0IHJsb2MgcnJlcyByd2VpIHJociBydGVtIiwiZXhwIjoxNjcwODA4MjIxLCJpYXQiOjE2NzAyMDM0MjF9.HXittzsGMOPGLdckfDLsxwhBYp3mFVq-1WMXheGck8A'
activity_id = 1010
client_id = "238H5R"
client_secret = "f53b6f2ea4e83c6a79bf2d36ea4a0609"
refresh_token = 'f5ea2cee03c2c300d08d5a4f41bcf9111762c2002666a2e2acca26a9ac4338db'

try:
    fitbit = api.Fitbit(client_id, client_secret, access_token=access_token, refresh_token=refresh_token)
except HTTPUnauthorized:
    pass


# activities = fitbit.activity_stats(qualifier='recent')
# pprint.pprint(activities)

# detail = fitbit.activity_detail(90009)
# print(detail)

results = pandas.DataFrame()
date = date(month=12, day=31, year=2021)
runs = fitbit.get_run_data(date, limit=100, after=True)
runs = runs["activities"]

for index, run in enumerate(runs):
    if run['activityTypeId'] == 90009:
        record = dict()
        record["log_id"] = run.get("logId")
        record["duration"] = run.get("activeDuration")
        record["ave heart rate"] = run.get("averageHeartRate")
        record["distance"] = run.get("distance")
        record["elev gain"] = run.get("elevationGain")
        record["start time"] = run.get("originalStartTime")
        for hr in run['heartRateZones']:
            if hr['name'] == "Fat Burn":
                record["fat_burn_minutes"] = hr["minutes"]
            elif hr['name'] == "Cardio":
                record["cardio_minutes"] = hr["minutes"]
            elif hr['name'] == "Peak":
                record["peak_minutes"] = hr["minutes"]
        record = pandas.DataFrame(record, index=[index])
        results = pandas.concat([results, record])

print(results.head())

client = pygsheets.authorize(service_account_file='gshees_credentials.json')
sheet = client.open_by_key('1FgdYRzID2F97qj_gdbswqfAR5jfWe1td92AEFz1KtBU')
wrksht = sheet.worksheet_by_title("Sheet1")
wrksht.set_dataframe(results, "A1", copy_head=True)
