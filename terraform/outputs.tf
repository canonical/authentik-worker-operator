# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

output "application" {
  description = "The deployed juju_application resource"
  value       = juju_application.authentik_worker
}

output "requires" {
  description = "Map of requires endpoint names"
  value = {
    authentik-cluster = "authentik-cluster"
    logging           = "logging"
    tracing           = "tracing"
  }
}

output "provides" {
  description = "Map of provides endpoint names"
  value = {
    metrics-endpoint = "metrics-endpoint"
  }
}
