# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Unit tests for integration wrappers."""

from unittest.mock import create_autospec

from charms.authentik_server.v0.authentik_cluster import AuthentikClusterRequirer
from charms.data_platform_libs.v0.data_interfaces import DatabaseRequires
from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer

from integrations import (
    AuthentikClusterIntegration,
    DatabaseConfig,
    TracingData,
)


class TestDatabaseConfig:
    """Tests for DatabaseConfig integration wrapper."""

    def test_load_parses_relation_data(self) -> None:
        """DatabaseConfig parses all required PostgreSQL relation fields."""
        from unittest.mock import MagicMock

        database = create_autospec(DatabaseRequires, instance=True)
        relation = MagicMock()
        relation.id = 1
        database.relations = [relation]
        database.fetch_relation_data.return_value = {
            1: {
                "endpoints": "test-host:5432",
                "username": "test-user",
                "password": "test-pass",
                "database": "authentik",
            }
        }
        config = DatabaseConfig.load(database)
        env = config.to_env_vars()
        assert env["AUTHENTIK_POSTGRESQL__HOST"] == "test-host"
        assert env["AUTHENTIK_POSTGRESQL__PORT"] == "5432"
        assert env["AUTHENTIK_POSTGRESQL__USER"] == "test-user"
        assert env["AUTHENTIK_POSTGRESQL__PASSWORD"] == "test-pass"
        assert env["AUTHENTIK_POSTGRESQL__NAME"] == "authentik"

    def test_load_returns_empty_when_no_relation(self) -> None:
        """DatabaseConfig returns empty when no relations exist."""
        database = create_autospec(DatabaseRequires, instance=True)
        database.relations = []
        config = DatabaseConfig.load(database)
        # When empty, load returns default empty config which maps to all-empty env
        assert config.host == ""
        assert config.port == ""
        env = config.to_env_vars()
        assert all(v == "" for v in env.values())

    def test_to_env_vars_returns_pg_env_vars(self) -> None:
        """DatabaseConfig env vars map endpoints to host and port correctly."""
        config = DatabaseConfig(
            host="test-host",
            port="5432",
            user="test-user",
            password="test-pass",
            name="authentik",
        )
        env = config.to_env_vars()
        assert env["AUTHENTIK_POSTGRESQL__HOST"] == "test-host"
        assert env["AUTHENTIK_POSTGRESQL__PORT"] == "5432"

    def test_is_ready_true_when_data_present(self) -> None:
        """DatabaseConfig.is_ready() is True when host and port are set."""
        config = DatabaseConfig(
            host="test-host",
            port="5432",
            user="test-user",
            password="test-pass",
            name="authentik",
        )
        assert config.is_ready()

    def test_is_ready_false_when_no_data(self) -> None:
        """DatabaseConfig.is_ready() is False when host or port is missing."""
        config = DatabaseConfig()
        assert not config.is_ready()


class TestAuthentikClusterIntegration:
    """Tests for AuthentikClusterIntegration wrapper."""

    def test_to_env_vars_returns_secret_key(self) -> None:
        """AuthentikClusterIntegration returns secret key in env vars when ready."""
        cluster = create_autospec(AuthentikClusterRequirer, instance=True)
        cluster.get_secret_key.return_value = "test-secret"
        cluster.is_ready = True
        integration = AuthentikClusterIntegration(cluster)
        env = integration.to_env_vars()
        assert env == {"AUTHENTIK_SECRET_KEY": "test-secret"}

    def test_to_env_vars_empty_when_not_ready(self) -> None:
        """AuthentikClusterIntegration returns empty dict when secret key is None."""
        cluster = create_autospec(AuthentikClusterRequirer, instance=True)
        cluster.get_secret_key.return_value = None
        cluster.is_ready = False
        integration = AuthentikClusterIntegration(cluster)
        env = integration.to_env_vars()
        assert env == {}


class TestTracingData:
    """Tests for TracingData integration wrapper."""

    def test_load_returns_empty_when_not_ready(self) -> None:
        """TracingData returns empty when tracing endpoint is not ready."""
        requirer = create_autospec(TracingEndpointRequirer, instance=True)
        requirer.is_ready.return_value = False
        tracing_data = TracingData.load(requirer)
        assert tracing_data.to_env_vars() == {}

    def test_load_returns_endpoint_when_ready(self) -> None:
        """TracingData is populated with endpoint when tracing is ready."""
        requirer = create_autospec(TracingEndpointRequirer, instance=True)
        requirer.is_ready.return_value = True
        requirer.get_endpoint.return_value = "http://tempo:4318"
        tracing_data = TracingData.load(requirer)
        assert tracing_data.is_ready
        assert tracing_data.endpoint == "http://tempo:4318"

    def test_to_env_vars_returns_otlp_endpoint_when_ready(self) -> None:
        """TracingData returns OTEL_EXPORTER_OTLP_ENDPOINT env var when ready."""
        requirer = create_autospec(TracingEndpointRequirer, instance=True)
        requirer.is_ready.return_value = True
        requirer.get_endpoint.return_value = "http://tempo:4318"
        tracing_data = TracingData.load(requirer)
        env = tracing_data.to_env_vars()
        assert "OTEL_EXPORTER_OTLP_ENDPOINT" in env
        assert env["OTEL_EXPORTER_OTLP_ENDPOINT"] == "http://tempo:4318"

    def test_to_env_vars_empty_when_not_ready(self) -> None:
        """TracingData returns empty dict when endpoint is not available."""
        requirer = create_autospec(TracingEndpointRequirer, instance=True)
        requirer.is_ready.return_value = False
        tracing_data = TracingData.load(requirer)
        assert tracing_data.to_env_vars() == {}
