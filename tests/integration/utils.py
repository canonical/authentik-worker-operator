# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

from contextlib import contextmanager
from typing import Callable, Iterator

import jubilant
import yaml
from integration.constants import APP_NAME
from tenacity import retry, stop_after_attempt, wait_exponential

StatusPredicate = Callable[[jubilant.Status], bool]


def get_unit_data(juju: jubilant.Juju, unit_name: str) -> dict:
    """Get the data for a given unit."""
    stdout = juju.cli("show-unit", unit_name)
    return yaml.safe_load(stdout)[unit_name]


def get_unit_address(juju: jubilant.Juju, app_name: str, unit_num: int = 0) -> str:
    """Get the address of a given unit."""
    return get_unit_data(juju, f"{app_name}/{unit_num}")["address"]


@contextmanager
def remove_integration(
    juju: jubilant.Juju, /, remote_app_name: str, integration_name: str
) -> Iterator[None]:
    """Temporarily remove an integration from the application.

    Integration is restored after the context manager exits.

    The pre-existing integration instance can still be "dying" when the ``finally`` block
    is called, so ``tenacity.retry`` is used to re-run ``juju integrate ...`` until the
    previous integration instance has finished dying.
    """

    @retry(
        wait=wait_exponential(multiplier=2, min=1, max=30),
        stop=stop_after_attempt(10),
        reraise=True,
    )
    def _reintegrate() -> None:
        juju.integrate(f"{APP_NAME}:{integration_name}", remote_app_name)

    juju.remove_relation(f"{APP_NAME}:{integration_name}", remote_app_name)
    try:
        yield
    finally:
        _reintegrate()


def all_active(*apps: str) -> StatusPredicate:
    """Return a predicate that checks all given apps are active."""
    return lambda status: jubilant.all_active(status, *apps)


def any_error(*apps: str) -> StatusPredicate:
    """Return a predicate that checks if any given app has an error."""
    return lambda status: jubilant.any_error(status, *apps)


def is_blocked(app: str) -> StatusPredicate:
    """Return a predicate that checks the given app is blocked."""
    return lambda status: status.apps[app].is_blocked


def unit_number(app: str, expected_num: int) -> StatusPredicate:
    """Return a predicate that checks the given app has the expected number of units."""
    return lambda status: len(status.apps[app].units) == expected_num


def and_(*predicates: StatusPredicate) -> StatusPredicate:
    """Return a predicate that is the logical AND of all given predicates."""
    return lambda status: all(predicate(status) for predicate in predicates)
