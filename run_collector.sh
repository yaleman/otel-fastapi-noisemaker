#!/bin/bash

# Runs the Splunk OpenTelemetry collector in docker

set -e

COLLECTOR_VERSION="0.104.0"

if [ -z "${SPLUNK_ACCESS_TOKEN}" ]; then
    echo "SPLUNK_ACCESS_TOKEN env var isn't set, exporter will not work!"
    exit 1
fi

if [ -z "${SPLUNK_REALM}" ]; then
    echo "SPLUNK_REALM env var isn't set, exporter will not work!"
    exit 1
fi

docker run --rm \
    -e "SPLUNK_ACCESS_TOKEN=${SPLUNK_ACCESS_TOKEN}" \
    -e "SPLUNK_REALM=${SPLUNK_REALM}" \
    -e "SPLUNK_LISTEN_INTERFACE=otel-collector" \
    --hostname otel-collector \
    --name noisemaker_otelcol \
    -p 127.0.0.1:4317:4317 \
    "quay.io/signalfx/splunk-otel-collector:${COLLECTOR_VERSION}" \
    --feature-gates "-component.UseLocalHostAsDefaultHost"