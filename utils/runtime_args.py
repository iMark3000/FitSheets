import argparse


def parse_runtime_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pick which ones")
    parser.add_argument(
        "-n", "--nutrition",
        help="Pulls nutrition data",
        dest="nutrition",
        action="store_true"
    )
    parser.add_argument(
        "-a", "--activity",
        help="Pulls activity data",
        dest="activity",
        action="store_true"
    )
    parser.add_argument(
        "-w", "--weight",
        help="Pulls weight log data",
        dest="weight",
        action="store_true"
    )
    parser.add_argument(
        "-s", "--sleep",
        help="Pulls sleep log data",
        dest="sleep",
        action="store_true"
    )
    parser.add_argument(
        "-r", "--refresh-token",
        help="Refreshes access token",
        dest="refresh_token",
        action="store_true"
    )
    parser.add_argument(
        "-d", "--days",
        help="Number of days to fetch; default 5",
        dest="days",
        default=5,
        type=int
    )

    return parser.parse_args()
