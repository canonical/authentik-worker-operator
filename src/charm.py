#!/usr/bin/env python3
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Charm the Authentik worker application."""

import logging

import ops
from charms.authentik_server.v0.authentik_cluster import AuthentikClusterRequirer
from charms.data_platform_libs.v0.data_interfaces import DatabaseRequires

from configs import CharmConfig
from constants import CLUSTER_RELATION, DATABASE_RELATION, WORKLOAD_CONTAINER
from integrations import AuthentikClusterIntegration, DatabaseIntegration
from services import PebbleService

logger = logging.getLogger(__name__)


class AuthentikWorkerCharm(ops.CharmBase):
    """Authentik Worker Operator."""

    def __init__(self, framework: ops.Framework) -> None:
        super().__init__(framework)

        self._container = self.unit.get_container(WORKLOAD_CONTAINER)
        self._pebble = PebbleService(self.unit)
        self._config = CharmConfig(self.config)

        self.database = DatabaseRequires(
            self, relation_name=DATABASE_RELATION, database_name="authentik"
        )
        self.cluster = AuthentikClusterRequirer(self, relation_name=CLUSTER_RELATION)

        self._db_integration = DatabaseIntegration(self.database)
        self._cluster_integration = AuthentikClusterIntegration(self.cluster)

        self.framework.observe(self.on.install, self._on_event)
        self.framework.observe(self.on.config_changed, self._on_event)
        self.framework.observe(self.on.authentik_pebble_ready, self._on_event)
        self.framework.observe(self.database.on.database_created, self._on_event)
        self.framework.observe(self.database.on.endpoints_changed, self._on_event)
        self.framework.observe(self.cluster.on.cluster_changed, self._on_event)
        self.framework.observe(self.cluster.on.cluster_removed, self._on_event)

        self.framework.observe(self.on.collect_unit_status, self._on_collect_status)

    def _on_event(self, event: ops.EventBase) -> None:
        self._reconcile()

    def _reconcile(self) -> None:
        """Idempotent reconciliation. Called on every event."""
        if not self._container.can_connect():
            return

        can_plan = all(
            [
                self._ensure_database(),
                self._ensure_cluster(),
            ]
        )
        if not can_plan:
            return

        layer = self._pebble.render_pebble_layer(
            self._db_integration,
            self._cluster_integration,
            self._config,
        )
        self._pebble.plan(layer)

    def _ensure_database(self) -> bool:
        """Return True if the database relation is ready."""
        return self._db_integration.is_ready()

    def _ensure_cluster(self) -> bool:
        """Return True if the cluster relation exists and data is ready."""
        if not self.model.get_relation(CLUSTER_RELATION):
            return False
        return self._cluster_integration.is_ready()

    def _on_collect_status(self, event: ops.CollectStatusEvent) -> None:
        """Report unit status."""
        if not self._container.can_connect():
            event.add_status(ops.WaitingStatus("waiting for pebble"))

        if not self._db_integration.is_ready():
            event.add_status(ops.BlockedStatus("missing pg-database relation"))

        if not self.model.get_relation(CLUSTER_RELATION):
            event.add_status(ops.BlockedStatus("missing authentik-cluster relation"))

        if not self.model.get_relation(CLUSTER_RELATION):
            event.add_status(ops.BlockedStatus("missing authentik-cluster relation"))

        if not self._cluster_integration.is_ready():
            event.add_status(ops.WaitingStatus("waiting for authentik-cluster data"))

        event.add_status(ops.ActiveStatus())


if __name__ == "__main__":  # pragma: nocover
    ops.main(AuthentikWorkerCharm)
