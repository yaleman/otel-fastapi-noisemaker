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

    try:
        res_json = res.json()
    except json.JSONDecodeError as error:
        print(
            f'JSON Error decoding response from url="{url}" error="{error}" response_body="{res.text}"',
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as error:
        print(
            f'Error decoding response from url="{url}" error="{error}" response_body="{res.text}"',
            file=sys.stderr,
        )
        sys.exit(1)

    if "data" not in res_json:
        print(f"No data key in response, got {json.dumps(res.text)}", file=sys.stderr)
        exit(1)

    data = res_json["data"]
    for node in data.get("nodes", []):
        node["entry_type"] = "node"
        print(json.dumps(node))

    for edge in data.get("edges", []):
        edge["entry_type"] = "edge"
        edge["serviceName"] = edge.get("fromNode", edge.get("serviceName", "<unknown>"))
        print(json.dumps(edge))


if __name__ == "__main__":
    main()
