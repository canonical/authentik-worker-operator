# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Unit tests for AuthentikWorkerCharm behavior."""

from unittest.mock import MagicMock, patch

import pytest
from ops import StatusBase, testing
from pytest_mock import MockerFixture
from unit.conftest import create_state

from constants import CLUSTER_RELATION, WORKLOAD_CONTAINER, WORKLOAD_SERVICE


class TestPebbleReadyEvent:
    """Tests for _on_pebble_ready side effects."""

    def test_open_port_called(
        self,
        context: testing.Context,
        container: testing.Container,
        mocked_open_port: MagicMock,
        mocked_holistic_handler: MagicMock,
        mocked_workload_service_version: MagicMock,
        all_satisfied_conditions: None,
    ) -> None:
        """Pebble-ready event opens the workload HTTP port."""
        state = create_state()

        context.run(context.on.pebble_ready(container), state)

        mocked_open_port.assert_called_once()

    def test_holistic_handler_called(
        self,
        context: testing.Context,
        container: testing.Container,
        mocked_open_port: MagicMock,
        mocked_holistic_handler: MagicMock,
        mocked_workload_service_version: MagicMock,
        all_satisfied_conditions: None,
    ) -> None:
        """Pebble-ready event delegates to the holistic handler."""
        state = create_state()

        context.run(context.on.pebble_ready(container), state)

        mocked_holistic_handler.assert_called_once()

    def test_workload_version_set(
        self,
        context: testing.Context,
        container: testing.Container,
        mocked_open_port: MagicMock,
        mocked_holistic_handler: MagicMock,
        mocked_workload_service_version: MagicMock,
        all_satisfied_conditions: None,
    ) -> None:
        """Pebble-ready event records the workload version on the unit."""
        state = create_state()

        state_out = context.run(context.on.pebble_ready(container), state)

        assert state_out.workload_version == mocked_workload_service_version.return_value


class TestEventRouting:
    """Tests that standard events are delegated to the holistic handler."""

    def test_config_changed_calls_holistic_handler(
        self,
        context: testing.Context,
        mocked_holistic_handler: MagicMock,
    ) -> None:
        state = create_state()

        context.run(context.on.config_changed(), state)

        mocked_holistic_handler.assert_called_once()

    def test_install_calls_holistic_handler(
        self,
        context: testing.Context,
        mocked_holistic_handler: MagicMock,
    ) -> None:
        state = create_state()

        context.run(context.on.install(), state)

        mocked_holistic_handler.assert_called_once()

    def test_cluster_changed_calls_holistic_handler(
        self,
        context: testing.Context,
        mocked_holistic_handler: MagicMock,
        cluster_relation_ready: testing.Relation,
        cluster_secret: testing.Secret,
    ) -> None:
        """cluster_changed library event (fired when secret_key_secret_id is published) routes to holistic handler."""
        state = create_state(relations=[cluster_relation_ready], secrets=[cluster_secret])

        # The AuthentikClusterRequirer fires cluster_changed on relation_changed when
        # secret_key_secret_id is present in the remote app databag.
        context.run(context.on.relation_changed(cluster_relation_ready), state)

        mocked_holistic_handler.assert_called_once()


class TestHolisticHandler:
    """Tests for _reconcile() guard conditions."""

    def test_when_pebble_not_ready_skips_planning(
        self,
        context: testing.Context,
        cluster_relation_ready: testing.Relation,
        cluster_secret: testing.Secret,
    ) -> None:
        """Reconciliation exits early when pebble container is not connectable."""
        state = create_state(
            can_connect=False, relations=[cluster_relation_ready], secrets=[cluster_secret]
        )

        state_out = context.run(context.on.config_changed(), state)

        assert not state_out.get_container(WORKLOAD_CONTAINER).plan.services

    def test_when_db_config_missing_skips_planning(
        self,
        context: testing.Context,
        cluster_relation_ready: testing.Relation,
    ) -> None:
        """Reconciliation exits early when cluster is ready but database config is missing from the secret."""
        empty_secret = testing.Secret({"secret-key": "test-secret-key"}, id="secret:abc123")
        state = create_state(relations=[cluster_relation_ready], secrets=[empty_secret])

        state_out = context.run(context.on.config_changed(), state)

        assert not state_out.get_container(WORKLOAD_CONTAINER).plan.services

    def test_when_all_ready_plans_pebble_layer(
        self,
        context: testing.Context,
        cluster_relation_ready: testing.Relation,
        cluster_secret: testing.Secret,
    ) -> None:
        """Reconciliation produces a non-empty Pebble plan when all guards pass."""
        state = create_state(
            relations=[cluster_relation_ready],
            secrets=[cluster_secret],
        )

        state_out = context.run(context.on.config_changed(), state)

        assert state_out.get_container(WORKLOAD_CONTAINER).plan.services

    def test_when_version_mismatch_skips_planning(
        self,
        context: testing.Context,
        cluster_secret: testing.Secret,
        mocked_workload_service_version: MagicMock,
    ) -> None:
        """Reconciliation is gated when the worker and server versions differ."""
        mocked_workload_service_version.return_value = "2026.1.0"
        cluster_rel_with_version = testing.Relation(
            CLUSTER_RELATION,
            interface="authentik_cluster",
            remote_app_name="authentik-server",
            remote_app_data={
                "secret_key_secret_id": cluster_secret.id,
                "server_version": "2026.2.0",
                "db_host": "test-host",
                "db_port": "5432",
                "db_user": "test-user",
                "db_name": "authentik",
            },
        )
        state = create_state(
            relations=[cluster_rel_with_version],
            secrets=[cluster_secret],
        )

        state_out = context.run(context.on.config_changed(), state)

        assert not state_out.get_container(WORKLOAD_CONTAINER).plan.services


class TestCollectStatusEvent:
    """Tests for _on_collect_status status path coverage."""

    def test_when_all_conditions_satisfied(
        self,
        context: testing.Context,
        all_satisfied_conditions: None,
        cluster_relation_ready: testing.Relation,
        cluster_secret: testing.Secret,
    ) -> None:
        state = create_state(relations=[cluster_relation_ready], secrets=[cluster_secret])

        state_out = context.run(context.on.collect_unit_status(), state)

        assert state_out.unit_status == testing.ActiveStatus()

    @pytest.mark.parametrize(
        "condition, condition_value, status, message",
        [
            (
                "container_connectivity",
                False,
                testing.WaitingStatus,
                "waiting for pebble",
            ),
            (
                "cluster_integration_exists",
                False,
                testing.BlockedStatus,
                f"missing {CLUSTER_RELATION} relation",
            ),
        ],
        ids=[
            "container_not_connected",
            "cluster_relation_missing",
        ],
    )
    def test_when_condition_fails(
        self,
        context: testing.Context,
        all_satisfied_conditions: None,
        condition: str,
        condition_value: bool,
        status: type[StatusBase],
        message: str,
    ) -> None:
        state = create_state()

        with patch(f"charm.{condition}", return_value=condition_value):
            state_out = context.run(context.on.collect_unit_status(), state)

        assert isinstance(state_out.unit_status, status)
        assert state_out.unit_status.message == message

    def test_when_db_data_absent_adds_waiting_status(
        self,
        context: testing.Context,
        cluster_relation_ready: testing.Relation,
    ) -> None:
        """WaitingStatus when cluster relation exists but database config is missing from the secret."""
        empty_secret = testing.Secret({"secret-key": "test-secret-key"}, id="secret:abc123")
        state = create_state(relations=[cluster_relation_ready], secrets=[empty_secret])

        state_out = context.run(context.on.collect_unit_status(), state)

        assert state_out.unit_status == testing.WaitingStatus(
            "waiting for database config from server"
        )

    def test_when_cluster_data_absent_adds_waiting_status(
        self,
        context: testing.Context,
        cluster_relation: testing.Relation,
        all_satisfied_conditions: None,
    ) -> None:
        """WaitingStatus when cluster relation exists but secret key not yet published."""
        state = create_state(relations=[cluster_relation])

        with patch("charm.cluster_integration_exists", return_value=True), patch(
            "charm.AuthentikClusterIntegration.is_ready", return_value=False
        ):
            state_out = context.run(context.on.collect_unit_status(), state)

        assert state_out.unit_status == testing.WaitingStatus("waiting for authentik-cluster data")

    def test_when_service_failing_adds_blocked_status(
        self,
        context: testing.Context,
        all_satisfied_conditions: None,
        mocked_is_failing: MagicMock,
    ) -> None:
        """BlockedStatus when the service is running but the ready check is down."""
        mocked_is_failing.return_value = True
        state = create_state()

        state_out = context.run(context.on.collect_unit_status(), state)

        assert state_out.unit_status == testing.BlockedStatus(
            "failed to start service, check container logs"
        )

    def test_when_service_not_running_adds_waiting_status(
        self,
        context: testing.Context,
        all_satisfied_conditions: None,
        mocked_is_running: MagicMock,
        cluster_relation_ready: testing.Relation,
        cluster_secret: testing.Secret,
    ) -> None:
        """WaitingStatus when service is not yet running."""
        mocked_is_running.return_value = False
        state = create_state(relations=[cluster_relation_ready], secrets=[cluster_secret])

        state_out = context.run(context.on.collect_unit_status(), state)

        assert state_out.unit_status == testing.WaitingStatus("waiting for service to start")

    def test_when_server_version_unknown_adds_waiting_status(
        self,
        context: testing.Context,
        all_satisfied_conditions: None,
        cluster_secret: testing.Secret,
    ) -> None:
        """WaitingStatus when the server has not yet published its version."""
        cluster_rel_no_version = testing.Relation(
            CLUSTER_RELATION,
            interface="authentik_cluster",
            remote_app_name="authentik-server",
            remote_app_data={
                "secret_key_secret_id": cluster_secret.id,
                "db_host": "test-host",
                "db_port": "5432",
                "db_user": "test-user",
                "db_name": "authentik",
            },
        )
        state = create_state(relations=[cluster_rel_no_version], secrets=[cluster_secret])

        state_out = context.run(context.on.collect_unit_status(), state)

        assert state_out.unit_status == testing.WaitingStatus(
            "waiting for server version to be published"
        )

    def test_when_version_mismatch_adds_blocked_status(
        self,
        context: testing.Context,
        all_satisfied_conditions: None,
        cluster_secret: testing.Secret,
        mocked_workload_service_version: MagicMock,
    ) -> None:
        """BlockedStatus when server version and worker version differ."""
        mocked_workload_service_version.return_value = "2026.1.0"
        cluster_rel_with_version = testing.Relation(
            CLUSTER_RELATION,
            interface="authentik_cluster",
            remote_app_name="authentik-server",
            remote_app_data={
                "secret_key_secret_id": cluster_secret.id,
                "server_version": "2026.2.0",
                "db_host": "test-host",
                "db_port": "5432",
                "db_user": "test-user",
                "db_name": "authentik",
            },
        )
        state = create_state(
            relations=[cluster_rel_with_version],
            secrets=[cluster_secret],
        )

        state_out = context.run(context.on.collect_unit_status(), state)

        assert isinstance(state_out.unit_status, testing.BlockedStatus)
        assert "version mismatch" in state_out.unit_status.message


class TestClusterIntegrationBroken:
    """Tests for cluster relation-broken side effects."""

    def test_stops_service_when_cluster_relation_broken(
        self,
        context: testing.Context,
        cluster_relation: testing.Relation,
        mocker: MockerFixture,
    ) -> None:
        """Cluster relation-broken event stops the workload service."""
        mock_stop = mocker.patch("ops.model.Container.stop")
        state = create_state(relations=[cluster_relation])

        context.run(context.on.relation_broken(cluster_relation), state)

        mock_stop.assert_called_once_with(WORKLOAD_SERVICE)

    def test_when_container_not_connected_does_not_raise(
        self,
        context: testing.Context,
        cluster_relation: testing.Relation,
    ) -> None:
        """Cluster relation-broken with disconnected container completes without error."""
        state = create_state(relations=[cluster_relation], can_connect=False)

        context.run(context.on.relation_broken(cluster_relation), state)
