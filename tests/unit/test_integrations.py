# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Unit tests for integration wrappers."""

from unittest.mock import create_autospec

from charms.authentik_server.v0.authentik_cluster import AuthentikClusterRequirer
from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer

from integrations import (
    AuthentikClusterIntegration,
    TracingData,
)


class TestAuthentikClusterIntegration:
    """Tests for AuthentikClusterIntegration wrapper."""

    def test_is_ready_true_when_all_ready(self) -> None:
        """AuthentikClusterIntegration is ready when cluster is ready and both secret key and database config exist."""
        cluster = create_autospec(AuthentikClusterRequirer, instance=True)
        cluster.is_ready.return_value = True
        cluster.get_secret_key.return_value = "test-secret"
        cluster.get_database_config.return_value = {
            "db-host": "test-host",
            "db-port": "5432",
            "db-user": "test-user",
            "db-password": "test-pass",
            "db-name": "authentik",
        }
        integration = AuthentikClusterIntegration(cluster)
        assert integration.is_ready()

    def test_is_ready_false_when_not_ready(self) -> None:
        """AuthentikClusterIntegration is not ready when cluster is not ready."""
        cluster = create_autospec(AuthentikClusterRequirer, instance=True)
        cluster.get_secret_key.return_value = None
        cluster.get_database_config.return_value = None
        integration = AuthentikClusterIntegration(cluster)
        assert not integration.is_ready()

    def test_is_ready_false_when_secret_key_missing(self) -> None:
        """AuthentikClusterIntegration is not ready when secret key is missing."""
        cluster = create_autospec(AuthentikClusterRequirer, instance=True)
        cluster.is_ready.return_value = True
        cluster.get_secret_key.return_value = None
        cluster.get_database_config.return_value = {
            "db-host": "test-host",
            "db-port": "5432",
            "db-user": "test-user",
            "db-password": "test-pass",
            "db-name": "authentik",
        }
        integration = AuthentikClusterIntegration(cluster)
        assert not integration.is_ready()

    def test_is_ready_false_when_database_config_missing(self) -> None:
        """AuthentikClusterIntegration is not ready when database config is missing."""
        cluster = create_autospec(AuthentikClusterRequirer, instance=True)
        cluster.is_ready.return_value = True
        cluster.get_secret_key.return_value = "test-secret"
        cluster.get_database_config.return_value = None
        integration = AuthentikClusterIntegration(cluster)
        assert not integration.is_ready()

    def test_to_env_vars_returns_all_env_vars(self) -> None:
        """AuthentikClusterIntegration maps all secret key and database variables to env vars when ready."""
        cluster = create_autospec(AuthentikClusterRequirer, instance=True)
        cluster.get_secret_key.return_value = "test-secret"
        cluster.get_database_config.return_value = {
            "db-host": "test-host",
            "db-port": "5432",
            "db-user": "test-user",
            "db-password": "test-pass",
            "db-name": "authentik",
        }
        integration = AuthentikClusterIntegration(cluster)
        env = integration.to_env_vars()
        assert env["AUTHENTIK_SECRET_KEY"] == "test-secret"
        assert env["AUTHENTIK_POSTGRESQL__HOST"] == "test-host"
        assert env["AUTHENTIK_POSTGRESQL__PORT"] == "5432"
        assert env["AUTHENTIK_POSTGRESQL__USER"] == "test-user"
        assert env["AUTHENTIK_POSTGRESQL__PASSWORD"] == "test-pass"
        assert env["AUTHENTIK_POSTGRESQL__NAME"] == "authentik"

    def test_to_env_vars_empty_when_not_ready(self) -> None:
        """AuthentikClusterIntegration returns empty dict when credentials are not available."""
        cluster = create_autospec(AuthentikClusterRequirer, instance=True)
        cluster.get_secret_key.return_value = None
        cluster.get_database_config.return_value = None
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
