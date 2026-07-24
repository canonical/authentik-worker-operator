#!/usr/bin/env python3
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Charm the Authentik worker application."""

import logging

import ops
from charms.authentik_server.v0.authentik_cluster import AuthentikClusterRequirer
from charms.loki_k8s.v1.loki_push_api import LogForwarder
from charms.observability_libs.v0.kubernetes_compute_resources_patch import (
    K8sResourcePatchFailedEvent,
    KubernetesComputeResourcesPatch,
    ResourceRequirements,
    adjust_resource_requirements,
)
from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer

from configs import CharmConfig
from constants import (
    CLUSTER_RELATION,
    LOGGING_RELATION,
    METRICS_RELATION,
    PEBBLE_READY_CHECK_NAME,
    TRACING_RELATION,
    WORKLOAD_CONTAINER,
    WORKLOAD_PORT,
    WORKLOAD_SERVICE,
)
from exceptions import PebbleError
from integrations import AuthentikClusterIntegration, TracingData
from services import PebbleService, WorkloadService
from utils import (
    NOOP_CONDITIONS,
    cluster_integration_exists,
    container_connectivity,
)

logger = logging.getLogger(__name__)


class AuthentikWorkerCharm(ops.CharmBase):
    """Authentik Worker Operator."""

    def __init__(self, framework: ops.Framework) -> None:
        super().__init__(framework)

        self._container = self.unit.get_container(WORKLOAD_CONTAINER)
        self._pebble = PebbleService(self.unit)
        self._workload_service = WorkloadService(self.unit)
        self._config = CharmConfig(self.config)

        self.cluster = AuthentikClusterRequirer(self, relation_name=CLUSTER_RELATION)
        self.log_forwarder = LogForwarder(self, relation_name=LOGGING_RELATION)
        self.metrics_endpoint = MetricsEndpointProvider(
            self,
            relation_name=METRICS_RELATION,
            jobs=[
                {
                    "job_name": "authentik_worker_metrics",
                    "static_configs": [{"targets": [f"*:{WORKLOAD_PORT}"]}],
                }
            ],
        )
        self.resources_patch = KubernetesComputeResourcesPatch(
            self,
            WORKLOAD_CONTAINER,
            resource_reqs_func=self._resource_reqs_from_config,
        )
        self.tracing_requirer = TracingEndpointRequirer(
            self,
            relation_name=TRACING_RELATION,
            protocols=["otlp_http"],
        )

        self._cluster_integration = AuthentikClusterIntegration(self.cluster)

        self.framework.observe(self.on.install, self._on_holistic_handler)
        self.framework.observe(self.on.config_changed, self._on_holistic_handler)
        self.framework.observe(self.on.authentik_pebble_ready, self._on_pebble_ready)
        self.framework.observe(self.on.authentik_pebble_check_failed, self._on_pebble_check_failed)
        self.framework.observe(
            self.on.authentik_pebble_check_recovered, self._on_pebble_check_recovered
        )
        self.framework.observe(self.cluster.on.cluster_changed, self._on_holistic_handler)
        self.framework.observe(
            self.cluster.on.cluster_removed, self._on_cluster_integration_broken
        )
        self.framework.observe(
            self.tracing_requirer.on.endpoint_changed, self._on_holistic_handler
        )
        self.framework.observe(
            self.tracing_requirer.on.endpoint_removed, self._on_holistic_handler
        )
        self.framework.observe(
            self.resources_patch.on.patch_failed, self._on_resource_patch_failed
        )
        self.framework.observe(self.on.update_status, self._on_holistic_handler)

        self.framework.observe(self.on.collect_unit_status, self._on_collect_status)

    def _on_holistic_handler(self, event: ops.EventBase) -> None:
        self.unit.status = ops.MaintenanceStatus("Configuring resources")
        self._holistic_handler(event)

    def _check_version_match(self) -> bool:
        """Return True if the worker's workload version matches the server's.

        Returns True (unblocked) when:
        - Both versions are identical and known.
        Returns False when versions are unknown or differ.
        """
        server_version = self.cluster.get_server_version()
        worker_version = self._workload_service.version
        if not server_version or not worker_version:
            logger.info(
                "Versions not yet fully known: server_version=%s, worker_version=%s",
                server_version,
                worker_version,
            )
            return False
        return server_version == worker_version

    def _holistic_handler(self, event: ops.EventBase) -> None:
        """Idempotent reconciliation. Called on every event."""
        if not all(condition(self) for condition in NOOP_CONDITIONS):
            self._stop_on_version_mismatch()
            return

        layer = self._pebble.render_pebble_layer(
            TracingData.load(self.tracing_requirer),
            self._cluster_integration,
            self._config,
        )
        try:
            self._pebble.plan(layer)
        except PebbleError as e:
            logger.error("Failed to plan pebble layer: %s", e)

    def _stop_on_version_mismatch(self) -> None:
        """Stop the workload when a definite server/worker version mismatch exists.

        A definite mismatch means both versions are known and differ; Authentik
        requires server/worker version parity, so a mismatched worker must not
        keep processing tasks. An unknown or not-yet-published version leaves the
        service untouched (it stays Waiting rather than Blocked).
        """
        server_version = self.cluster.get_server_version()
        worker_version = self._workload_service.version
        if not (server_version and worker_version and server_version != worker_version):
            return
        if not self._container.can_connect():
            return
        try:
            self._container.get_service(WORKLOAD_SERVICE)
        except ops.ModelError:
            return
        try:
            self._container.stop(WORKLOAD_SERVICE)
        except ops.pebble.Error:
            logger.warning("Failed to stop workload after version mismatch")

    def _resource_reqs_from_config(self) -> ResourceRequirements:
        """Build resource requirements from charm config."""
        limits = {
            "cpu": self.model.config.get("cpu"),
            "memory": self.model.config.get("memory"),
        }
        return adjust_resource_requirements(
            limits,
            {"cpu": "100m", "memory": "200Mi"},
            adhere_to_requests=True,
        )

    def _on_resource_patch_failed(self, event: K8sResourcePatchFailedEvent) -> None:
        """Handle kubernetes resource patch failures and retry reconciliation."""
        logger.error("Resource patching failed: %s", event.message)
        self._on_holistic_handler(event)

    def _on_pebble_ready(self, event: ops.PebbleReadyEvent) -> None:
        """Handle pebble-ready by opening ports, reconciling, and setting version."""
        self._workload_service.open_port()
        self._on_holistic_handler(event)
        self._workload_service.set_version()

    def _on_pebble_check_failed(self, event: ops.PebbleCheckFailedEvent) -> None:
        """Log when the worker ready check fails."""
        if event.info.name == PEBBLE_READY_CHECK_NAME:
            logger.warning("Workload check failed: %s", event.info.name)

    def _on_pebble_check_recovered(self, event: ops.PebbleCheckRecoveredEvent) -> None:
        """Re-drive reconciliation and status when the worker ready check recovers."""
        if event.info.name == PEBBLE_READY_CHECK_NAME:
            logger.info("Workload check recovered: %s", event.info.name)
            self._on_holistic_handler(event)

    def _on_cluster_integration_broken(self, event: ops.RelationBrokenEvent) -> None:
        """Stop service when authentik-cluster integration is removed."""
        if self._container.can_connect():
            try:
                self._container.stop(WORKLOAD_SERVICE)
            except ops.pebble.Error:
                logger.warning("Failed to stop workload after cluster relation broken")

    def _check_db_status(self) -> ops.StatusBase:
        """Check database integration status."""
        if self._cluster_integration.is_ready():
            return ops.ActiveStatus()

        # If the cluster relation itself is ready, but database config specifically is missing
        if self.cluster.is_ready() and not self._cluster_integration.is_database_config_ready():
            return ops.WaitingStatus("waiting for database config from server")
        return ops.ActiveStatus()

    def _check_cluster_status(self) -> ops.StatusBase:
        """Check cluster integration status."""
        if not cluster_integration_exists(self):
            return ops.BlockedStatus("missing authentik-cluster relation")

        if not self._cluster_integration.is_ready():
            # If the database config specifically is missing, let db_status handle it
            if (
                self.cluster.is_ready()
                and not self._cluster_integration.is_database_config_ready()
            ):
                return ops.ActiveStatus()
            return ops.WaitingStatus("waiting for authentik-cluster data")

        server_version = self.cluster.get_server_version()
        worker_version = self._workload_service.version
        if server_version and worker_version and server_version != worker_version:
            return ops.BlockedStatus(
                f"version mismatch: server={server_version}, worker={worker_version}"
            )
        if not server_version:
            return ops.WaitingStatus("waiting for server version to be published")

        return ops.ActiveStatus()

    def _on_collect_status(self, event: ops.CollectStatusEvent) -> None:
        """Report unit status."""
        can_connect = container_connectivity(self)
        if not can_connect:
            event.add_status(ops.WaitingStatus("waiting for pebble"))

        event.add_status(self._check_db_status())
        event.add_status(self._check_cluster_status())

        if (
            can_connect
            and cluster_integration_exists(self)
            and self._cluster_integration.is_ready()
        ):
            if self._workload_service.is_failing():
                event.add_status(
                    ops.BlockedStatus("failed to start service, check container logs")
                )
            elif not self._workload_service.is_running():
                event.add_status(ops.WaitingStatus("waiting for service to start"))

        if patch_status := self.resources_patch.get_status():
            event.add_status(patch_status)
        event.add_status(ops.ActiveStatus())


if __name__ == "__main__":  # pragma: nocover
    ops.main(AuthentikWorkerCharm)
