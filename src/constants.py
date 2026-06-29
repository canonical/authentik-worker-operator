# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Constants for the Authentik worker charm."""

WORKLOAD_CONTAINER = "authentik"
WORKLOAD_SERVICE = "authentik-worker"
COMMAND = "/lifecycle/ak worker"
PEBBLE_READY_CHECK_NAME = "ready"
WORKLOAD_PORT: int = 9000
HTTP_PORT: int = WORKLOAD_PORT


CLUSTER_RELATION = "authentik-cluster"
LOGGING_RELATION = "logging"
TRACING_RELATION = "tracing"
METRICS_RELATION = "metrics-endpoint"
