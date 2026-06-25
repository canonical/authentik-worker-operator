# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Reusable charm condition helpers."""

from typing import TYPE_CHECKING, Callable

from constants import CLUSTER_RELATION, WORKLOAD_CONTAINER

if TYPE_CHECKING:
    from charm import AuthentikWorkerCharm

Condition = Callable[["AuthentikWorkerCharm"], bool]


def container_connectivity(charm: "AuthentikWorkerCharm") -> bool:
    """Return whether the workload container is reachable."""
    return charm.unit.get_container(WORKLOAD_CONTAINER).can_connect()


def cluster_integration_exists(charm: "AuthentikWorkerCharm") -> bool:
    """Return whether an authentik-cluster relation exists."""
    return bool(charm.model.get_relation(CLUSTER_RELATION))


def cluster_integration_is_ready(charm: "AuthentikWorkerCharm") -> bool:
    """Return whether the cluster integration is ready and has all credentials."""
    return charm._cluster_integration.is_ready()


def version_is_matched(charm: "AuthentikWorkerCharm") -> bool:
    """Return whether the worker's workload version matches the server's."""
    return charm._check_version_match()


NOOP_CONDITIONS: tuple[Condition, ...] = (
    container_connectivity,
    cluster_integration_exists,
    cluster_integration_is_ready,
    version_is_matched,
)
