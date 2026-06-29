# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Unit tests for CharmConfig."""

import pytest

from configs import CharmConfig


class TestCharmConfig:
    @pytest.fixture
    def full_config(self) -> dict:
        return {
            "log_level": "debug",
            "worker_processes": 4,
            "worker_threads": 8,
            "task_max_retries": 10,
            "task_default_time_limit": 1200,
            "task_expiration_days": 15,
            "http_proxy": "http://proxy:6666",
            "https_proxy": "http://proxy:6666",
            "no_proxy": "localhost",
        }

    @pytest.fixture
    def minimal_config(self) -> dict:
        return {
            "log_level": "info",
        }

    def test_to_env_vars(self, full_config: dict) -> None:
        config = CharmConfig(full_config)
        env = config.to_env_vars()

        assert env["AUTHENTIK_LOG_LEVEL"] == "debug"
        assert env["AUTHENTIK_WORKER__PROCESSES"] == "4"
        assert env["AUTHENTIK_WORKER__THREADS"] == "8"
        assert env["AUTHENTIK_WORKER__TASK_MAX_RETRIES"] == "10"
        assert env["AUTHENTIK_WORKER__TASK_DEFAULT_TIME_LIMIT"] == "seconds=1200"
        assert env["AUTHENTIK_WORKER__TASK_EXPIRATION"] == "days=15"
        assert env["HTTP_PROXY"] == "http://proxy:6666"
        assert env["HTTPS_PROXY"] == "http://proxy:6666"
        assert env["NO_PROXY"] == "localhost"

    def test_to_env_vars_defaults(self, minimal_config: dict) -> None:
        config = CharmConfig(minimal_config)
        env = config.to_env_vars()

        assert env["AUTHENTIK_LOG_LEVEL"] == "info"
        assert env["AUTHENTIK_WORKER__PROCESSES"] == "1"
        assert env["AUTHENTIK_WORKER__THREADS"] == "2"
        assert env["AUTHENTIK_WORKER__TASK_MAX_RETRIES"] == "5"
        assert env["AUTHENTIK_WORKER__TASK_DEFAULT_TIME_LIMIT"] == "seconds=600"
        assert env["AUTHENTIK_WORKER__TASK_EXPIRATION"] == "days=30"
        assert "HTTP_PROXY" not in env
        assert "HTTPS_PROXY" not in env
        assert "NO_PROXY" not in env
