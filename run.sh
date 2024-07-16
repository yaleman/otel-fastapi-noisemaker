#!/bin/bash

if [ -z "${SERVICE_PORT}" ]; then
    export SERVICE_PORT="9290";
fi

export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"

export SERVICE_ENVIRONMENT="noisemaker"
export SERVICE_HOSTNAME="noisemaker"
export OTEL_SERVICE_NAME="NoiseMaker"

export OTEL_RESOURCE_ATTRIBUTES="service.namespace=${SERVICE_NAMESPACE},deployment.environment=${SERVICE_ENVIRONMENT},host.name=${SERVICE_HOSTNAME}"

export OTEL_PYTHON_FASTAPI_EXCLUDED_URLS="/healthcheck,/ws,/metrics"

# https://www.uvicorn.org/deployment/
poetry run opentelemetry-instrument \
    uvicorn otel_fastapi_noisemaker:app \
        --host "127.0.0.1" --port "${SERVICE_PORT}" \
        --forwarded-allow-ips '*' \
        --proxy-headers
