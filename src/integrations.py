# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Wrappers for charm relation data, implementing EnvVarConvertible."""

import logging
from dataclasses import dataclass

from charms.authentik_server.v0.authentik_cluster import AuthentikClusterRequirer
from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer

from env_vars import EnvVars

logger = logging.getLogger(__name__)


class AuthentikClusterIntegration:
    """Reads authentik-cluster relation data and exposes it as env vars.

    Args:
        cluster: The AuthentikClusterRequirer library object.
    """

    def __init__(self, cluster: AuthentikClusterRequirer) -> None:
        self._cluster = cluster

    def is_ready(self) -> bool:
        """Return True if the cluster relation is ready and all credentials are available."""
        return bool(self._cluster.get_secret_key() and self._cluster.get_database_config())

    def is_database_config_ready(self) -> bool:
        """Return True if the database configuration is available."""
        return self._cluster.get_database_config() is not None

    def to_env_vars(self) -> EnvVars:
        """Return the secret key and database environment variables."""
        secret_key = self._cluster.get_secret_key()
        cfg = self._cluster.get_database_config()
        if not secret_key or not cfg:
            return {}
        return {
            "AUTHENTIK_SECRET_KEY": secret_key,
            "AUTHENTIK_POSTGRESQL__HOST": cfg.get("db-host", ""),
            "AUTHENTIK_POSTGRESQL__PORT": cfg.get("db-port", ""),
            "AUTHENTIK_POSTGRESQL__USER": cfg.get("db-user", ""),
            "AUTHENTIK_POSTGRESQL__PASSWORD": cfg.get("db-password", ""),
            "AUTHENTIK_POSTGRESQL__NAME": cfg.get("db-name", ""),
        }


@dataclass(frozen=True, slots=True)
class TracingData:
    """Holds tracing endpoint data and exposes it as env vars."""

    is_ready: bool = False
    endpoint: str = ""

    def to_env_vars(self) -> EnvVars:
        """Return tracing endpoint environment variables when tracing is ready."""
        if not self.is_ready:
            return {}
        return {"OTEL_EXPORTER_OTLP_ENDPOINT": self.endpoint}

    @classmethod
    def load(cls, requirer: TracingEndpointRequirer) -> "TracingData":
        """Construct TracingData from tracing relation data."""
        if not requirer.is_ready():
            return cls()
        endpoint = requirer.get_endpoint("otlp_http")
        return cls(is_ready=True, endpoint=endpoint or "")
