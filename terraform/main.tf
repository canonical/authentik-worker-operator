# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

/**
 * # Terraform module for the authentik-worker charm
 *
 * This is a Terraform module facilitating the deployment of the authentik-worker
 * charm using the Juju Terraform provider.
 */

resource "juju_application" "authentik_worker" {
  name        = var.app_name
  model_uuid  = var.model_uuid
  config      = var.config
  constraints = var.constraints
  units       = var.units
  resources   = var.resources
  trust       = true

  charm {
    name     = "authentik-worker"
    base     = var.base
    channel  = var.channel
    revision = var.revision
  }
}
