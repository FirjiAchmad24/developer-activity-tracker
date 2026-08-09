import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, time
from zoneinfo import ZoneInfo


GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"
TIMEZONE = ZoneInfo("Asia/Makassar")

USERNAME = os.getenv("GITHUB_USERNAME", "FirjiAchmad24")
TOKEN = os.getenv("GH_ACTIVITY_TOKEN")


def build_date_range():
    now = datetime.now(TIMEZONE)
    today = now.date()

    start = datetime.combine(
        today,
        time(0, 0, 0),
        tzinfo=TIMEZONE,
    )

    end = datetime.combine(
        today,
        time(23, 59, 59),
        tzinfo=TIMEZONE,
    )

    return today, start.isoformat(), end.isoformat()


def query_github_contributions(start_date, end_date):
    if not TOKEN:
        raise RuntimeError(
            "GH_ACTIVITY_TOKEN is not available."
        )

    query = """
    query(
        $login: String!,
        $from: DateTime!,
        $to: DateTime!
    ) {
        user(login: $login) {
            contributionsCollection(
                from: $from,
                to: $to
            ) {
                contributionCalendar {
                    totalContributions
                    weeks {
                        contributionDays {
                            date
                            contributionCount
                        }
                    }
                }
            }
        }
    }
    """

    payload = {
        "query": query,
        "variables": {
            "login": USERNAME,
            "from": start_date,
            "to": end_date,
        },
    }

    request = urllib.request.Request(
        GITHUB_GRAPHQL_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "developer-activity-tracker",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=30,
        ) as response:
            return json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as error:
        body = error.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"GitHub API HTTP error {error.code}: {body}"
        ) from error

    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Unable to connect to GitHub API: {error}"
        ) from error


def get_contribution_count(response, target_date):
    if response.get("errors"):
        messages = [
            error.get("message", "Unknown GraphQL error")
            for error in response["errors"]
        ]

        raise RuntimeError(
            "GitHub GraphQL error: "
            + "; ".join(messages)
        )

    user = response.get("data", {}).get("user")

    if user is None:
        raise RuntimeError(
            f"GitHub user '{USERNAME}' was not found."
        )

    calendar = (
        user["contributionsCollection"]
        ["contributionCalendar"]
    )

    target = target_date.isoformat()

    for week in calendar["weeks"]:
        for day in week["contributionDays"]:
            if day["date"] == target:
                return day["contributionCount"]

    return 0


def write_github_output(has_activity, count, date):
    output_file = os.getenv("GITHUB_OUTPUT")

    if not output_file:
        return

    with open(
        output_file,
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            f"has_activity={str(has_activity).lower()}\n"
        )
        file.write(
            f"contribution_count={count}\n"
        )
        file.write(
            f"activity_date={date.isoformat()}\n"
        )


def main():
    print("===================================")
    print("GitHub Contribution Checker")
    print("===================================")
    print(f"GitHub user : {USERNAME}")

    today, start_date, end_date = build_date_range()

    print(f"Date        : {today.isoformat()}")
    print(f"Timezone    : Asia/Makassar")
    print()

    try:
        response = query_github_contributions(
            start_date,
            end_date,
        )

        contribution_count = get_contribution_count(
            response,
            today,
        )

    except RuntimeError as error:
        print(f"ERROR: {error}")
        print()
        print(
            "Activity check failed. "
            "Fallback activity will NOT be generated."
        )

        sys.exit(1)

    has_activity = contribution_count > 0

    print(
        f"Contributions today: "
        f"{contribution_count}"
    )

    if has_activity:
        print("GitHub activity detected.")
        print("Fallback activity is not required.")
    else:
        print("No GitHub contribution detected today.")
        print("Fallback activity may be generated.")

    write_github_output(
        has_activity,
        contribution_count,
        today,
    )


if __name__ == "__main__":
    main()
