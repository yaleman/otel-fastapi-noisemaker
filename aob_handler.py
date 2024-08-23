# encoding = utf-8

import sys
import json
import datetime
from typing import Any

"""
    IMPORTANT
    Edit only the validate_input and collect_events functions.
    Do not edit any other part in this file.
    This file is generated only once when creating the modular input.
"""
"""
# For advanced users, if you want to create single instance mod input, uncomment this method.
def use_single_instance_mode():
    return True
"""


def validate_input(helper: Any, definition: Any) -> None:
    """Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    # realm = definition.parameters.get('realm', None)
    # access_token = definition.parameters.get('access_token', None)
    # look_back_time_hours = definition.parameters.get('look_back_time_hours', None)
    # environment = definition.parameters.get('environment', None)
    pass


def collect_events(helper: Any, ew: Any) -> None:
    """Implement your data collection logic here"""

    # The following examples get the arguments of this input.
    # Note, for single instance mod input, args will be returned as a dict.
    # For multi instance mod input, args will be returned as a single value.
    opt_realm = helper.get_arg("realm")
    opt_access_token = helper.get_arg("access_token")
    opt_look_back_time_hours = helper.get_arg("look_back_time_hours")
    opt_environment = helper.get_arg("environment")

    # set the log level for this modular input
    # (log_level can be "debug", "info", "warning", "error" or "critical", case insensitive)
    helper.set_log_level("INFO")

    try:
        hours_back = int(opt_look_back_time_hours)
    except ValueError as error:
        helper.log_error(
            f"Error converting look_back_time_hours={opt_look_back_time_hours} to int: {error}"
        )
        sys.exit(1)
    earliest = (
        datetime.datetime.now(datetime.timezone.utc)
        - datetime.timedelta(hours=hours_back)
    ).isoformat()
    latest = datetime.datetime.now(datetime.timezone.utc).isoformat()

    url = f"https://api.{opt_realm}.signalfx.com/v2/apm/topology"
    headers = {"X-SF-Token": opt_access_token, "Content-Type": "application/json"}
    payload = {
        "timeRange": f"{earliest}/{latest}",
        "tagFilters": [
            {
                "name": "sf_environment",
                "operator": "equals",
                "scope": "GLOBAL",
                "value": opt_environment,
            }
        ],
    }
    # The following examples send rest requests to some endpoint.
    try:
        res = helper.send_http_request(
            url,
            "POST",
            payload=payload,
            headers=headers,
            verify=True,
            timeout=90,
            use_proxy=True,
        )

    except Exception as error:
        helper.log_error(
            f'Error querying url="{url}" error="{error}" response_body="{res.text}"',
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
        event = helper.new_event(
            json.dumps(node, default=str, ensure_ascii=False),
            time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            index=helper.get_output_index(),
            source=helper.get_input_type(),
            sourcetype=helper.get_sourcetype(),
            done=True,
            unbroken=True,
        )
        helper.log_debug(f"Node: {event}")
        ew.write_event(event)

    for edge in data.get("edges", []):
        edge["entry_type"] = "edge"
        edge["serviceName"] = edge.get("fromNode", edge.get("serviceName", "<unknown>"))

        event = helper.new_event(
            json.dumps(edge, default=str, ensure_ascii=False),
            time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            index=helper.get_output_index(),
            source=helper.get_input_type(),
            sourcetype=helper.get_sourcetype(),
            done=True,
            unbroken=True,
        )
        helper.log_debug(f"Edge: {event}")
        ew.write_event(event)
