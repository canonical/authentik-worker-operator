# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Constants for the Authentik worker charm."""

WORKLOAD_CONTAINER = "authentik"
SERVICE_NAME = "authentik-worker"
COMMAND = "ak worker"

DATABASE_RELATION = "pg-database"
CLUSTER_RELATION = "authentik-cluster"
