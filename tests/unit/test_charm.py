# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.
#
# To learn more about testing, see https://documentation.ubuntu.com/ops/latest/explanation/testing/

import pytest
from charm import CONTAINER_NAME, SERVICE_NAME, AuthentikWorkerCharm
from ops import pebble, testing

CHECK_NAME = "service-ready"  # Name of Pebble check in the mock workload container.

layer = pebble.Layer(
    {
        "services": {
            SERVICE_NAME: {
                "override": "replace",
                "command": "/lifecycle/ak worker",
                "startup": "enabled",
            }
        },
        "checks": {
            CHECK_NAME: {
                "override": "replace",
                "level": "ready",
                "threshold": 3,
                "startup": "enabled",
                "http": {
                    "url": "http://localhost:9000/outpost.goauthentik.io/ping",
                },
            }
        },
    }
)


def mock_get_version():
    """Get a mock version string without executing the workload code."""
    return "2024.12.0"


def test_pebble_ready(monkeypatch: pytest.MonkeyPatch):
    """Test that the charm has the correct state after handling the pebble-ready event."""
    # Arrange:
    ctx = testing.Context(AuthentikWorkerCharm)
    check_in = testing.CheckInfo(
        CHECK_NAME,
        level=pebble.CheckLevel.READY,
        status=pebble.CheckStatus.UP,
    )
    container_in = testing.Container(
        CONTAINER_NAME,
        can_connect=True,
        layers={"base": layer},
        service_statuses={SERVICE_NAME: pebble.ServiceStatus.INACTIVE},
        check_infos={check_in},
    )
    state_in = testing.State(containers={container_in})
    monkeypatch.setattr("charm.authentik_worker.get_version", mock_get_version)

    # Act:
    state_out = ctx.run(ctx.on.pebble_ready(container_in), state_in)

    # Assert:
    container_out = state_out.get_container(container_in.name)
    assert container_out.service_statuses[SERVICE_NAME] == pebble.ServiceStatus.ACTIVE
    assert state_out.workload_version is not None
    assert state_out.unit_status == testing.ActiveStatus()


def test_pebble_ready_service_not_ready():
    """Test that the charm raises an error if the workload isn't ready after Pebble starts it."""
    # Arrange:
    ctx = testing.Context(AuthentikWorkerCharm)
    check_in = testing.CheckInfo(
        CHECK_NAME,
        level=pebble.CheckLevel.READY,
        status=pebble.CheckStatus.DOWN,
    )
    container_in = testing.Container(
        CONTAINER_NAME,
        can_connect=True,
        layers={"base": layer},
        service_statuses={SERVICE_NAME: pebble.ServiceStatus.INACTIVE},
        check_infos={check_in},
    )
    state_in = testing.State(containers={container_in})

    # Act & assert:
    with pytest.raises(testing.errors.UncaughtCharmError):
        ctx.run(ctx.on.pebble_ready(container_in), state_in)
