# OTEL FastAPI Noisemaker

Testing what it looks like to self-spam to show off usage.

## Running it

You need to set the following environment variables so the OTEL collector will work:

- SPLUNK_ACCESS_TOKEN
- SPLUNK_REALM

Then ensure you have Python (3.12+), `poetry` and Docker/Orbstack/something containery installed, then:

  1. `./run_collector.sh` in its own shell - That'll start the Splunk OTEL collector in Docker.
  2. In a new tab/shell run the server:
     1. `poetry install` - To build the virtual environment.
     2. `poetry run opentelemetry-bootstrap --action=install` to set up OpenTelemetry things.
     3. `./run.sh` - Runs the server.
  3. In another tab/shell, send some traffic:
     1. `poetry run make_noise -c 1 -r 1` to send a "single client, single request" test.
