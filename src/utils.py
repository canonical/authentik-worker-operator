# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Reusable charm condition helpers."""

from typing import TYPE_CHECKING, Callable

from constants import CLUSTER_RELATION, DATABASE_RELATION, WORKLOAD_CONTAINER

if TYPE_CHECKING:
    from charm import AuthentikWorkerCharm

Condition = Callable[["AuthentikWorkerCharm"], bool]


def container_connectivity(charm: "AuthentikWorkerCharm") -> bool:
    """Return whether the workload container is reachable."""
    return charm.unit.get_container(WORKLOAD_CONTAINER).can_connect()


def database_integration_exists(charm: "AuthentikWorkerCharm") -> bool:
    """Return whether a database relation exists."""
    return bool(charm.model.relations[DATABASE_RELATION])


def database_resource_is_created(charm: "AuthentikWorkerCharm") -> bool:
    """Return whether the database resource has been created by the provider."""
    return charm.database.is_resource_created()


def cluster_integration_exists(charm: "AuthentikWorkerCharm") -> bool:
    """Return whether an authentik-cluster relation exists."""
    return bool(charm.model.get_relation(CLUSTER_RELATION))


NOOP_CONDITIONS: tuple[Condition, ...] = (
    container_connectivity,
    database_integration_exists,
    database_resource_is_created,
)
