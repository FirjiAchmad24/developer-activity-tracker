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


def create_daily_log(now):
    year = now.strftime("%Y")
    month = now.strftime("%m")
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    monthly_dir = ACTIVITY_DIR / year
    monthly_dir.mkdir(parents=True, exist_ok=True)

    monthly_file = monthly_dir / f"{month}.md"

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
    data["total_automated_entries"] += 1
    data["last_activity"] = now.strftime("%Y-%m-%d")
    data["last_automated_activity"] = now.isoformat()

    return data


def main():
    now = datetime.now(TIMEZONE)

    data = load_activity_data()

    create_daily_log(now)

    data = update_metadata(data, now)

    save_activity_data(data)

    print("Developer activity updated successfully.")
    print(f"Date: {now.strftime('%Y-%m-%d')}")
    print(f"Time: {now.strftime('%H:%M:%S')} WITA")


if __name__ == "__main__":
    main()
