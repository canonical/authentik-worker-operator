# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Wrappers for charm relation data, implementing EnvVarConvertible."""

import logging
from dataclasses import dataclass

from charms.authentik_server.v0.authentik_cluster import AuthentikClusterRequirer
from charms.data_platform_libs.v0.data_interfaces import DatabaseRequires
from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer

from env_vars import EnvVars

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DatabaseConfig:
    """Holds PostgreSQL relation data and exposes it as env vars."""

    host: str = ""
    port: str = ""
    user: str = ""
    password: str = ""
    name: str = ""

    def to_env_vars(self) -> EnvVars:
        """Return PostgreSQL connection environment variables."""
        return {
            "AUTHENTIK_POSTGRESQL__HOST": self.host,
            "AUTHENTIK_POSTGRESQL__PORT": self.port,
            "AUTHENTIK_POSTGRESQL__USER": self.user,
            "AUTHENTIK_POSTGRESQL__PASSWORD": self.password,
            "AUTHENTIK_POSTGRESQL__NAME": self.name,
        }

    def is_ready(self) -> bool:
        """Return True when required relation fields are available."""
        return bool(self.host and self.port and self.user)

    @classmethod
    def load(cls, database: DatabaseRequires) -> "DatabaseConfig":
        """Construct DatabaseConfig from relation data.

        Args:
            database: The DatabaseRequires relation wrapper.

        Returns:
            A populated DatabaseConfig or a default one if relation data is incomplete.
        """
        if not (relations := database.relations):
            return cls()
        integration_data = database.fetch_relation_data()[relations[0].id]
        if "endpoints" not in integration_data:
            return cls()
        host, port = integration_data["endpoints"].split(":")
        return cls(
            host=host,
            port=port,
            user=integration_data.get("username", ""),
            password=integration_data.get("password", ""),
            name=integration_data.get("database", ""),
        )


class AuthentikClusterIntegration:
    """Reads authentik-cluster relation data and exposes it as env vars.

    Args:
        cluster: The AuthentikClusterRequirer library object.
    """

    def __init__(self, cluster: AuthentikClusterRequirer) -> None:
        self._cluster = cluster

    def is_ready(self) -> bool:
        """Return True if the cluster relation is ready and the secret key is available."""
        return self._cluster.is_ready()

    def to_env_vars(self) -> EnvVars:
        """Return the secret key environment variable."""
        secret_key = self._cluster.get_secret_key()
        if not secret_key:
            return {}
        return {"AUTHENTIK_SECRET_KEY": secret_key}


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
