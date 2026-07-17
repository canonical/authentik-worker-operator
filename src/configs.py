# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Charm configuration wrapper."""

from ops import ConfigData

from env_vars import EnvVars


class CharmConfig:
    """Wraps charm config and exposes it as env vars.

    Args:
        config: The ops ConfigData object from the charm.
    """

    def __init__(self, config: ConfigData) -> None:
        self._config = config

    def to_env_vars(self) -> EnvVars:
        """Return charm-config-derived environment variables."""
        env_vars: dict[str, str] = {
            "AUTHENTIK_LOG_LEVEL": self._config.get("log_level", "info"),
            "AUTHENTIK_WORKER__PROCESSES": str(self._config.get("worker_processes", 1)),
            "AUTHENTIK_WORKER__THREADS": str(self._config.get("worker_threads", 2)),
            "AUTHENTIK_WORKER__TASK_MAX_RETRIES": str(self._config.get("task_max_retries", 5)),
            "AUTHENTIK_WORKER__TASK_DEFAULT_TIME_LIMIT": f"seconds={self._config.get('task_default_time_limit', 600)}",
            "AUTHENTIK_WORKER__TASK_EXPIRATION": f"days={self._config.get('task_expiration_days', 30)}",
            # Connection pooling and task signaling
            "AUTHENTIK_POSTGRESQL__DISABLE_SERVER_SIDE_CURSORS": str(
                self._config.get("postgresql_disable_server_side_cursors", False)
            ).lower(),
            "AUTHENTIK_POSTGRESQL__CONN_HEALTH_CHECKS": str(
                self._config.get("postgresql_conn_health_checks", False)
            ).lower(),
            "AUTHENTIK_POSTGRESQL__CONN_MAX_AGE": str(
                self._config.get("postgresql_conn_max_age", 0)
            ),
            "AUTHENTIK_WORKER__CONSUMER_LISTEN_TIMEOUT": str(
                self._config.get("consumer_listen_timeout", 30)
            ),
        }

        if http_proxy := self._config.get("http_proxy"):
            env_vars["HTTP_PROXY"] = http_proxy
        if https_proxy := self._config.get("https_proxy"):
            env_vars["HTTPS_PROXY"] = https_proxy
        if no_proxy := self._config.get("no_proxy"):
            env_vars["NO_PROXY"] = no_proxy

        return env_vars
