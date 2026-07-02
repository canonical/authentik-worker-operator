# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

import os
import subprocess
from pathlib import Path
from typing import Generator

import jubilant
import pytest
import requests
from integration.constants import APP_NAME, DB_APP, SERVER_APP
from integration.utils import get_unit_address

from src.constants import CLUSTER_RELATION


@pytest.fixture(scope="session")
def charm() -> Path:
    """Return the path of the charm under test, building it if necessary."""
    charm_path = os.getenv("CHARM_PATH")
    if charm_path:
        return Path(charm_path)
    subprocess.run(["charmcraft", "pack"], check=True)
    charms = list(Path(".").glob("*.charm"))
    if not charms:
        raise RuntimeError("No .charm file found after charmcraft pack")
    return charms[0].absolute()


@pytest.fixture
def http_client() -> Generator[requests.Session, None, None]:
    """Provide an HTTP client with TLS verification disabled."""
    with requests.Session() as client:
        client.verify = False
        yield client


def integrate_dependencies(juju: jubilant.Juju) -> None:
    """Integrate the charm with all required dependencies."""
    juju.integrate(DB_APP, SERVER_APP)
    juju.integrate(f"{SERVER_APP}:{CLUSTER_RELATION}", APP_NAME)


@pytest.fixture
def public_address(juju: jubilant.Juju) -> str:
    """Return the public address of the authentik-worker unit."""
    return get_unit_address(juju, app_name=APP_NAME)
