import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


TIMEZONE = ZoneInfo("Asia/Makassar")

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT_DIR / "data" / "activity.json"
ACTIVITY_DIR = ROOT_DIR / "activity"


def load_activity_data():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_activity_data(data):
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
        file.write("\n")


def get_monthly_file(now):
    year = now.strftime("%Y")
    month = now.strftime("%m")

    monthly_dir = ACTIVITY_DIR / year
    monthly_dir.mkdir(parents=True, exist_ok=True)

    return monthly_dir / f"{month}.md"


def activity_already_recorded(data, now):
    today = now.strftime("%Y-%m-%d")

    # Primary check using metadata.
    if data.get("last_activity") == today:
        return True

    # Secondary safeguard by checking the monthly log.
    monthly_file = get_monthly_file(now)

    if monthly_file.exists():
        content = monthly_file.read_text(encoding="utf-8")

        row_identifier = f"| {today} |"

        if row_identifier in content:
            return True

    return False


def create_daily_log(now):
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    monthly_file = get_monthly_file(now)

    if not monthly_file.exists():
        monthly_file.write_text(
            f"# Developer Activity — {now.strftime('%B %Y')}\n\n"
            "| Date | Time | Type | Description |\n"
            "|---|---|---|---|\n",
            encoding="utf-8",
        )

    entry = (
        f"| {date} | {time} WITA | Automated | "
        "Scheduled developer activity tracker execution |\n"
    )

    with monthly_file.open("a", encoding="utf-8") as file:
        file.write(entry)


def update_metadata(data, now):
    data["total_automated_entries"] = (
        data.get("total_automated_entries", 0) + 1
    )

    data["last_activity"] = now.strftime("%Y-%m-%d")
    data["last_automated_activity"] = now.isoformat()

    return data


def main():
    now = datetime.now(TIMEZONE)

    print("===================================")
    print("Developer Activity Tracker")
    print("===================================")
    print(f"Current date : {now.strftime('%Y-%m-%d')}")
    print(f"Current time : {now.strftime('%H:%M:%S')} WITA")
    print()

    data = load_activity_data()

    if activity_already_recorded(data, now):
        print("Activity already recorded for today.")
        print("No new automated activity will be generated.")
        return

    create_daily_log(now)

    data = update_metadata(data, now)

    save_activity_data(data)

    print("Developer activity generated successfully.")
    print(f"Activity date: {now.strftime('%Y-%m-%d')}")
    print(
        f"Total automated entries: "
        f"{data['total_automated_entries']}"
    )


if __name__ == "__main__":
    main()
