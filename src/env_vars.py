# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Default environment variables and EnvVarConvertible protocol."""

from typing import Mapping, Protocol, TypeAlias, Union

EnvVars: TypeAlias = Mapping[str, Union[str, bool]]

DEFAULT_WORKER_ENV: dict[str, str | bool] = {
    "AUTHENTIK_ERROR_REPORTING__ENABLED": "false",
    "AUTHENTIK_LOG_LEVEL": "info",
    # Upstream container and Python execution environment variables
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONUNBUFFERED": "1",
    "VIRTUAL_ENV": "/ak-root/.venv",
    "VENV_PATH": "/ak-root/.venv",
    "PYTHONPATH": "/",
    "AK_RUNNING_IN_CONTAINER": "true",
    "GOFIPS": "1",
    # The ak lifecycle script calls `python` which only exists in the venv.
    # Juju's charm layer uses override:replace, discarding the rock's PATH.
    "PATH": "/lifecycle:/ak-root/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    # PostgreSQL — populated by DatabaseConfig
    "AUTHENTIK_POSTGRESQL__HOST": "",
    "AUTHENTIK_POSTGRESQL__PORT": "",
    "AUTHENTIK_POSTGRESQL__USER": "",
    "AUTHENTIK_POSTGRESQL__PASSWORD": "",
    "AUTHENTIK_POSTGRESQL__NAME": "",
    "AUTHENTIK_POSTGRESQL__DISABLE_SERVER_SIDE_CURSORS": "false",
    "AUTHENTIK_POSTGRESQL__CONN_HEALTH_CHECKS": "false",
    "AUTHENTIK_POSTGRESQL__CONN_MAX_AGE": "0",
    "AUTHENTIK_WORKER__CONSUMER_LISTEN_TIMEOUT": "30",
    # Cluster secret — populated by AuthentikClusterIntegration
    "AUTHENTIK_SECRET_KEY": "",
    # Update check — always disabled in charm-managed deployments
    "AUTHENTIK_DISABLE_UPDATE_CHECK": "true",
    # Proxy
    "HTTP_PROXY": "",
    "HTTPS_PROXY": "",
    "NO_PROXY": "",
}


class EnvVarConvertible(Protocol):
    """Interface for objects that contribute environment variables to the Pebble layer."""

    def to_env_vars(self) -> EnvVars:
        """Return a mapping of environment variable names to values."""
        ...
