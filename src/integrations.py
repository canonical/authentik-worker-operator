# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Wrappers for charm relation data, implementing EnvVarConvertible."""

import logging

from charms.authentik_server.v0.authentik_cluster import AuthentikClusterRequirer
from charms.data_platform_libs.v0.data_interfaces import DatabaseRequires

from env_vars import EnvVars

logger = logging.getLogger(__name__)


class DatabaseIntegration:
    """Reads PostgreSQL relation data and exposes it as env vars.

    Args:
        database: The DatabaseRequires library object.
    """

    def __init__(self, database: DatabaseRequires) -> None:
        self._database = database

    def is_ready(self) -> bool:
        """Return True if the database relation is present and has endpoint data."""
        return bool(self._get_connection())

    def _get_connection(self) -> dict[str, str] | None:
        """Return a connection dict or None if the relation is not ready."""
        for data in self._database.fetch_relation_data().values():
            if "endpoints" in data:
                host, port = data["endpoints"].split(":")
                return {
                    "host": host,
                    "port": port,
                    "user": data["username"],
                    "password": data["password"],
                    "name": data["database"],
                }
        return None

    def to_env_vars(self) -> EnvVars:
        """Return PostgreSQL connection environment variables."""
        conn = self._get_connection()
        if not conn:
            return {}
        return {
            "AUTHENTIK_POSTGRESQL__HOST": conn["host"],
            "AUTHENTIK_POSTGRESQL__PORT": conn["port"],
            "AUTHENTIK_POSTGRESQL__USER": conn["user"],
            "AUTHENTIK_POSTGRESQL__PASSWORD": conn["password"],
            "AUTHENTIK_POSTGRESQL__NAME": conn["name"],
        }


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
