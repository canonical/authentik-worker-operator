# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

from pathlib import Path

import yaml

METADATA = yaml.safe_load(Path("./charmcraft.yaml").read_text())
APP_NAME = METADATA["name"]
APP_IMAGE = METADATA["resources"]["oci-image"]["upstream-source"]

DB_APP = "postgresql-k8s"
DB_CHANNEL = "16/stable"

TRAEFIK_APP = "traefik-k8s"
TRAEFIK_CHANNEL = "latest/edge"

SERVER_APP = "authentik-server"
SERVER_CHANNEL = "latest/edge"

CA_APP = "self-signed-certificates"
CA_CHANNEL = "latest/stable"
