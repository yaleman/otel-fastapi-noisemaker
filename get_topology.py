from datetime import UTC, datetime, timedelta
import json
import os
import sys

import click
import requests


@click.command()
@click.option(
    "-r",
    "--realm",
    help="Splunk realm to query",
    default=os.getenv("SPLUNK_REALM", "us0"),
)
@click.option("-e", "--environment", help="Environment to query", default="*")
@click.option("-d", "--days-back", help="Number of days back to query", default=1)
def main(realm: str, environment: str, days_back: int) -> None:
    token = os.getenv("API_TOKEN")
    if token is None:
        print("Can't get API_TOKEN env var, can't continue!", file=sys.stderr)
        sys.exit(1)

    url = f"https://api.{realm}.signalfx.com/v2/apm/topology"

    headers = {"X-SF-Token": token}

    earliest = (datetime.now(UTC) - timedelta(days=days_back)).isoformat()
    latest = datetime.now(UTC).isoformat()

    payload = {
        "timeRange": f"{earliest}/{latest}",
        "tagFilters": [
            {
                "name": "sf_environment",
                "operator": "equals",
                "scope": "GLOBAL",
                "value": environment,
            }
        ],
    }

    try:
        res = requests.post(url, headers=headers, json=payload)
        res.raise_for_status()
    except Exception as error:
        print(
            f'Error querying url="{url}" error="{error}" response_body="{res.text}"',
            file=sys.stderr,
        )
        sys.exit(1)

    print(json.dumps(res.json()))


if __name__ == "__main__":
    main()
