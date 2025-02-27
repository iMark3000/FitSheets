"""
DATA_CONFIGURATIONS
--- Key of DATA_CONFIGURATIONS is the metric being pulled from FitBit
--- sheet_name is the name of the worksheet in the Google Spreadsheet
--- id_field is the unique identifier of record in teh worksheet;
        FitBit fields need to be renamed to match id_field
--- field_mappings maps the FitBit field to the column headers of the worksheet
--- field_filter_and_order filters the fields and is the order that the fields
        are in on the worksheet; Must be renamed first
"""

DATA_CONFIGURATIONS = {
    "SLEEP_": {
        "sheet_name": "",
        "id_field": "Log ID",
        "field_mappings": {
            "awakeCount": "Awake Count",
            "awakeDuration": "Awake Duration",
            "awakeningsCount": "Awakenings Count",
            "dateOfSleep": "Date of Sleep",
            "duration": "Duration",
            "efficiency": "Efficiency",
            "endTime": "End Time",
            "isMainSleep": "Is Main Sleep",
            "logId": "Log ID",
            "minutesAfterWakeup": "Min After Wakeup",
            "minutesAsleep": "Min Asleep",
            "minutesAwake": "Min Awake",
            "minutesToFallAsleep": "Min To Fall Asleep",
            "restlessCount": "Restless Count",
            "restlessDuration": "Restless Duration",
            "startTime": "Start Time"
        },
        "field_filter_and_order": [
            "Log ID",
            "Is Main Sleep",
            "Date of Sleep",
            "Start Time"
            "End Time",
            "Duration",
            "Efficiency",
            "Min To Fall Asleep",
            "Min Asleep",
            "Min Awake",
            "Min After Wakeup",
            "Awake Count",
            "Awake Duration",
            "Awakenings Count",
            "Restless Count",
            "Restless Duration",
        ]
    },
    "NUTRITION": {
        "sheet_name": "Nutrition",
        "id_field": "Date",
        "field_mappings": {
            "date": "Date",
            "summary.calories": "Calories In",
            "goals.calories": "Calorie Goal",
            "summary.carbs": "Carbs",
            "summary.fat": "Fat",
            "summary.fiber": "Fiber",
            "summary.protein": "Protein",
            "summary.sodium": "Sodium",
            "summary.water": "Water"
        },
        "field_filter_and_order": [
            "Date",
            "Calorie Goal",
            "Calories In",
            "Protein",
            "Carbs",
            "Fat",
            "Fiber",
            "Sodium",
            "Water"
        ],
        "timestamp_cell": "A1"
    },
    "WEIGHT": {
        "sheet_name": "",
        "id_field": "",
        "field_mappings": {
        },
        "field_filter_and_order": []
    },
    "ACTIVITY": {
        "sheet_name": "",
        "id_field": "",
        "field_mappings": {
        },
        "field_filter_and_order": []
    }
}

