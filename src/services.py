# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Services module for the Authentik worker charm."""

import copy
import logging

from ops import ModelError, Unit
from ops.pebble import CheckStatus
from ops.pebble import ConnectionError as PebbleConnectionError
from ops.pebble import Layer, LayerDict

from constants import (
    COMMAND,
    HTTP_PORT,
    PEBBLE_READY_CHECK_NAME,
    WORKLOAD_CONTAINER,
    WORKLOAD_SERVICE,
)
from env_vars import DEFAULT_WORKER_ENV, EnvVarConvertible
from exceptions import PebbleError

logger = logging.getLogger(__name__)

PEBBLE_LAYER_DICT: LayerDict = {
    "summary": "authentik-worker-operator layer",
    "description": "pebble config layer for authentik-worker-operator",
    "services": {
        WORKLOAD_SERVICE: {
            "override": "replace",
            "summary": "Authentik worker",
            "command": COMMAND,
            "startup": "disabled",
        }
    },
    "checks": {
        "alive": {
            "override": "replace",
            "level": "alive",
            "threshold": 60,
            "http": {
                "url": f"http://localhost:{HTTP_PORT}/-/health/live/",
            },
        },
        PEBBLE_READY_CHECK_NAME: {
            "override": "replace",
            "level": "ready",
            "threshold": 60,
            "http": {
                "url": f"http://localhost:{HTTP_PORT}/-/health/ready/",
            },
        },
    },
}


class PebbleService:
    """Manages the workload Pebble layer for the Authentik worker.

    Args:
        unit: The Juju unit owning the workload container.
    """

    def __init__(self, unit: Unit) -> None:
        self._unit = unit
        self._container = unit.get_container(WORKLOAD_CONTAINER)
        self._layer_dict: LayerDict = copy.deepcopy(PEBBLE_LAYER_DICT)

    def plan(self, layer: Layer) -> None:
        """Apply a Pebble layer and replan the container.

        Args:
            layer: The Pebble layer to apply.

        Raises:
            PebbleError: If the service fails to start.
        """
        self._container.add_layer(WORKLOAD_SERVICE, layer, combine=True)
        try:
            if not self._container.get_service(WORKLOAD_SERVICE).is_running():
                self._container.start(WORKLOAD_SERVICE)
            else:
                self._container.replan()
        except Exception as e:
            raise PebbleError(f"Pebble failed to replan the workload service. Error: {e}")

    def render_pebble_layer(self, *env_var_sources: EnvVarConvertible) -> Layer:
        """Render a Pebble layer merging env vars from all sources.

        Precedence: DEFAULT_WORKER_ENV is the base; each successive source's
        ``to_env_vars()`` output is merged on top (last one wins).
        Intended order (lowest → highest priority): database, cluster, config.

        Args:
            *env_var_sources: Objects implementing EnvVarConvertible.

        Returns:
            The rendered Pebble Layer.
        """
        env_vars: dict[str, str | bool] = dict(DEFAULT_WORKER_ENV)
        for source in env_var_sources:
            env_vars.update(source.to_env_vars())
        self._layer_dict["services"][WORKLOAD_SERVICE]["environment"] = env_vars
        return Layer(self._layer_dict)


class WorkloadService:
    """Service helper for runtime interactions with the workload."""

    def __init__(self, unit: Unit) -> None:
        self._unit = unit
        self._container = unit.get_container(WORKLOAD_CONTAINER)

    @property
    def version(self) -> str:
        """Workload version reported by the binary, or empty on failure."""
        try:
            process = self._container.exec(
                [
                    "/ak-root/.venv/bin/python",
                    "-c",
                    "from authentik import VERSION; print(VERSION)",
                ],
                environment={"PYTHONPATH": "/"},
            )
            return process.wait_output()[0].strip()
        except Exception:
            return ""

    def set_version(self) -> None:
        """Set the workload version on the unit, logging failures without raising."""
        try:
            self._unit.set_workload_version(self.version)
        except Exception as e:
            logger.error("Failed to set workload version: %s", e)

    def open_port(self) -> None:
        """Open workload HTTP port."""
        self._unit.open_port(protocol="tcp", port=HTTP_PORT)

    def is_running(self) -> bool:
        """Return True when service is running and the ready check is up."""
        try:
            service = self._container.get_service(WORKLOAD_SERVICE)
        except (ModelError, PebbleConnectionError) as e:
            logger.error("Failed to get pebble service: %s", e)
            return False

        if not service.is_running():
            return False

        c = self._container.get_checks().get(PEBBLE_READY_CHECK_NAME)
        if not c:
            return False
        return c.status == CheckStatus.UP

    def is_failing(self) -> bool:
        """Return True when service is running and the ready check is down."""
        try:
            service = self._container.get_service(WORKLOAD_SERVICE)
        except (ModelError, PebbleConnectionError):
            return False

        if not service.is_running():
            return False

        c = self._container.get_checks().get(PEBBLE_READY_CHECK_NAME)
        if not c:
            return False
        return c.status == CheckStatus.DOWN
