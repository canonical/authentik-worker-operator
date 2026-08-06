# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Unit tests for PebbleService and WorkloadService helpers."""

from unittest.mock import MagicMock

import ops
import pytest
from ops.pebble import CheckStatus

from constants import PEBBLE_READY_CHECK_NAME, WORKLOAD_SERVICE
from exceptions import PebbleError
from services import PebbleService, WorkloadService


def _unit_with_container(container: MagicMock) -> MagicMock:
    """Return a mock unit whose workload container is ``container``."""
    unit = MagicMock()
    unit.get_container.return_value = container
    return unit


@pytest.fixture(autouse=True)
def mocked_workload_service_version() -> None:
    """Override the conftest autouse mock so the real version property is exercised."""
    return None


class TestPebbleServicePlan:
    """Tests for PebbleService.plan error handling."""

    def test_add_layer_error_becomes_pebble_error(self) -> None:
        """A pebble error raised by add_layer is wrapped in PebbleError."""
        container = MagicMock()
        container.add_layer.side_effect = ops.pebble.Error("bad layer")
        service = PebbleService(_unit_with_container(container))

        with pytest.raises(PebbleError):
            service.plan(MagicMock())

    def test_replan_error_becomes_pebble_error(self) -> None:
        """A pebble error raised while starting the service is wrapped in PebbleError."""
        container = MagicMock()
        container.get_service.return_value.is_running.return_value = False
        container.start.side_effect = ops.pebble.Error("cannot start")
        service = PebbleService(_unit_with_container(container))

        with pytest.raises(PebbleError):
            service.plan(MagicMock())

    def test_plan_starts_service_when_not_running(self) -> None:
        """Add the layer and start the service when it is not running."""
        container = MagicMock()
        container.get_service.return_value.is_running.return_value = False
        layer = MagicMock()
        service = PebbleService(_unit_with_container(container))

        service.plan(layer)

        container.add_layer.assert_called_once_with(WORKLOAD_SERVICE, layer, combine=True)
        container.start.assert_called_once_with(WORKLOAD_SERVICE)
        container.replan.assert_not_called()

    def test_plan_replans_when_already_running(self) -> None:
        """Replan the container when the service is already running."""
        container = MagicMock()
        container.get_service.return_value.is_running.return_value = True
        service = PebbleService(_unit_with_container(container))

        service.plan(MagicMock())

        container.replan.assert_called_once()
        container.start.assert_not_called()


class TestWorkloadServiceVersion:
    """Tests for WorkloadService.version memoization."""

    def test_version_is_fetched_once(self) -> None:
        """The workload version is fetched from the container only once."""
        container = MagicMock()
        container.exec.return_value.wait_output.return_value = ("2026.2.2\n", "")
        service = WorkloadService(_unit_with_container(container))

        first = service.version
        second = service.version

        assert first == "2026.2.2"
        assert second == "2026.2.2"
        container.exec.assert_called_once()

    def test_version_empty_on_failure_is_memoized(self) -> None:
        """A failed version fetch returns empty and is not retried."""
        container = MagicMock()
        container.exec.side_effect = ops.pebble.Error("exec failed")
        service = WorkloadService(_unit_with_container(container))

        assert service.version == ""
        assert service.version == ""
        container.exec.assert_called_once()


class TestWorkloadServiceIsRunning:
    """Tests for WorkloadService.is_running success guard."""

    def _service_with_check(self, status: CheckStatus, successes: int | None) -> WorkloadService:
        container = MagicMock()
        container.get_service.return_value.is_running.return_value = True
        check = MagicMock()
        check.status = status
        check.successes = successes
        container.get_checks.return_value = {PEBBLE_READY_CHECK_NAME: check}
        return WorkloadService(_unit_with_container(container))

    def test_running_when_up_and_has_successes(self) -> None:
        """is_running is True when the check is UP and has recorded successes."""
        service = self._service_with_check(CheckStatus.UP, 3)

        assert service.is_running() is True

    def test_running_when_up_but_no_successes(self) -> None:
        """is_running is True when the check is UP even with zero successes on first start."""
        service = self._service_with_check(CheckStatus.UP, 0)

        assert service.is_running() is True

    def test_running_when_successes_none(self) -> None:
        """is_running is True when the check is UP and reports no successes field."""
        service = self._service_with_check(CheckStatus.UP, None)

        assert service.is_running() is True

    def test_not_running_when_check_down(self) -> None:
        """is_running is False when the ready check is DOWN even with successes."""
        service = self._service_with_check(CheckStatus.DOWN, 3)

        assert service.is_running() is False
