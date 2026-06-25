# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Shared unit-test helpers."""

from typing import Any
from unittest.mock import MagicMock, PropertyMock

import pytest
import pytest_mock
from ops import testing

from charm import AuthentikWorkerCharm
from constants import CLUSTER_RELATION, WORKLOAD_CONTAINER


# ---------------------------------------------------------------------------
# create_state() — module-level factory (NOT a fixture)
# ---------------------------------------------------------------------------
def create_state(
    *,
    leader: bool = True,
    secrets: list | None = None,
    relations: list | None = None,
    containers: list | None = None,
    config: dict | None = None,
    can_connect: bool = True,
    workload_version: str = "2026.2.2",
) -> testing.State:
    """Build a complete State with sensible defaults for authentik-worker tests.

    Args:
        leader: Whether this unit is the leader.
        secrets: Secrets present in model state.
        relations: Relation endpoints present in model state.
        containers: Explicit container state. If omitted, a default workload
            container is built from ``can_connect``.
        config: Charm config values.
        can_connect: Whether the default workload container can connect.
        workload_version: Unused — kept for API compatibility with callers that
            pass it; version is read from the workload binary at runtime.

    Returns:
        A populated Scenario state object.
    """
    if containers is None:
        containers = [testing.Container(WORKLOAD_CONTAINER, can_connect=can_connect)]
    return testing.State(
        leader=leader,
        secrets=list(secrets or []),
        relations=list(relations or []),
        containers=list(containers),
        config=config or {},
    )


# ---------------------------------------------------------------------------
# Resource-patch mocks (autouse)
# ---------------------------------------------------------------------------
@pytest.fixture()
def mocked_resource_patch(mocker: pytest_mock.MockerFixture) -> MagicMock:
    """Mock the resource patcher backing library to avoid real API interactions."""
    mocked = mocker.patch(
        "charms.observability_libs.v0.kubernetes_compute_resources_patch.ResourcePatcher",
        autospec=True,
    )
    mocked.return_value.is_failed.return_value = (False, "")
    mocked.return_value.is_in_progress.return_value = False
    return mocked


@pytest.fixture(autouse=True)
def mocked_k8s_resource_patch(
    mocker: pytest_mock.MockerFixture, mocked_resource_patch: MagicMock
) -> None:
    """Patch KubernetesComputeResourcesPatch behavior used by the charm."""
    mocker.patch.multiple(
        "charm.KubernetesComputeResourcesPatch",
        _namespace="testing",
        _patch=lambda *a, **kw: True,
        is_ready=lambda *a, **kw: True,
    )


# ---------------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------------
@pytest.fixture
def context() -> testing.Context:
    """Return a scenario context for the charm under test."""
    return testing.Context(AuthentikWorkerCharm)


# ---------------------------------------------------------------------------
# Container fixture
# ---------------------------------------------------------------------------
@pytest.fixture
def container() -> testing.Container:
    """Return a default authentik workload container test double."""
    return testing.Container(WORKLOAD_CONTAINER, can_connect=True)


# ---------------------------------------------------------------------------
# Relation fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def cluster_relation() -> testing.Relation:
    """Return an authentik-cluster relation without remote data (not yet ready)."""
    return testing.Relation(
        CLUSTER_RELATION,
        interface="authentik_cluster",
        remote_app_name="authentik-server",
    )


@pytest.fixture
def cluster_secret() -> testing.Secret:
    """Return the Juju secret carrying the authentik secret key and database config."""
    return testing.Secret(
        {
            "secret-key": "test-secret-key",
            "db-host": "test-host",
            "db-port": "5432",
            "db-user": "test-user",
            "db-password": "test-pass",
            "db-name": "authentik",
        },
        id="secret:abc123",
    )


@pytest.fixture
def cluster_relation_ready(cluster_secret: testing.Secret) -> testing.Relation:
    """Return an authentik-cluster relation with the secret key published."""
    return testing.Relation(
        CLUSTER_RELATION,
        interface="authentik_cluster",
        remote_app_name="authentik-server",
        remote_app_data={
            "secret_key_secret_id": cluster_secret.id,
            "server_version": "2026.2.2",
        },
    )


# ---------------------------------------------------------------------------
# Charm service mocks
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def mocked_workload_service_version(mocker: pytest_mock.MockerFixture) -> MagicMock:
    """Mock WorkloadService.version to return a fixed string without exec."""
    return mocker.patch(
        "charm.WorkloadService.version", new_callable=PropertyMock, return_value="2026.2.2"
    )


@pytest.fixture
def mocked_holistic_handler(mocker: pytest_mock.MockerFixture) -> MagicMock:
    """Replace _on_holistic_handler with a mock to isolate event-routing tests."""
    mock_fn = MagicMock()

    def _on_holistic_handler(self: Any, event: Any) -> None:
        mock_fn(event)

    mocker.patch("charm.AuthentikWorkerCharm._on_holistic_handler", _on_holistic_handler)
    return mock_fn


@pytest.fixture
def mocked_open_port(mocker: pytest_mock.MockerFixture) -> MagicMock:
    """Mock WorkloadService.open_port to avoid real socket operations."""
    return mocker.patch("charm.WorkloadService.open_port")


@pytest.fixture
def mocked_is_running(mocker: pytest_mock.MockerFixture) -> MagicMock:
    """Mock WorkloadService.is_running to return True by default."""
    return mocker.patch("charm.WorkloadService.is_running", return_value=True)


@pytest.fixture
def mocked_is_failing(mocker: pytest_mock.MockerFixture) -> MagicMock:
    """Mock WorkloadService.is_failing to return False by default."""
    return mocker.patch("charm.WorkloadService.is_failing", return_value=False)


# ---------------------------------------------------------------------------
# Condition mock fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def mocked_container_connectivity(mocker: pytest_mock.MockerFixture) -> MagicMock:
    """Mock container_connectivity condition to return True."""
    return mocker.patch("charm.container_connectivity", return_value=True)


@pytest.fixture
def mocked_cluster_integration_exists(mocker: pytest_mock.MockerFixture) -> MagicMock:
    """Mock cluster_integration_exists condition to return True."""
    return mocker.patch("charm.cluster_integration_exists", return_value=True)


@pytest.fixture
def mocked_cluster_integration_is_ready(mocker: pytest_mock.MockerFixture) -> MagicMock:
    """Mock AuthentikClusterIntegration.is_ready to return True."""
    return mocker.patch("charm.AuthentikClusterIntegration.is_ready", return_value=True)


@pytest.fixture
def all_satisfied_conditions(
    mocked_container_connectivity: MagicMock,
    mocked_cluster_integration_exists: MagicMock,
    mocked_cluster_integration_is_ready: MagicMock,
    mocked_is_running: MagicMock,
    mocked_is_failing: MagicMock,
) -> None:
    """Activate all condition mocks so that every guard passes by default."""
