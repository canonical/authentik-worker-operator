# charmcraft-config Specification

## Purpose
Defines the `charmcraft.yaml` contract for the Authentik Worker charm: the
workload container, the OCI image it draws from, the integration endpoints it
declares, and the non-root execution settings the rock requires.
## Requirements
### Requirement: Container name matches WORKLOAD_CONTAINER constant
The `charmcraft.yaml` containers section SHALL declare a container named `authentik`, matching
the `WORKLOAD_CONTAINER = "authentik"` constant in `constants.py`. No container named
`authentik-worker` SHALL exist.

#### Scenario: Container name is correct
- **WHEN** `charmcraft.yaml` is parsed
- **THEN** the containers section contains exactly one entry with key `authentik`
- **THEN** no entry with key `authentik-worker` exists

### Requirement: OCI image points to the canonical upstream source
The `oci-image` resource `upstream-source` SHALL be set to
`ghcr.io/canonical/authentik-server:2026.5.3`. The worker uses the same
Canonical-built authentik-server rock as the server charm, launched with the
worker command rather than the server command.

#### Scenario: Image reference is correct
- **WHEN** `charmcraft.yaml` is parsed
- **THEN** `resources.oci-image.upstream-source` equals `ghcr.io/canonical/authentik-server:2026.5.3`

### Requirement: authentik-cluster relation is declared
The `charmcraft.yaml` SHALL declare an `authentik-cluster` relation under `requires` with
interface `authentik_cluster` and `optional: true`.

#### Scenario: Relation is present
- **WHEN** `charmcraft.yaml` is parsed
- **THEN** `requires.authentik-cluster.interface` equals `authentik_cluster`
- **THEN** `requires.authentik-cluster.optional` is `true`

### Requirement: No database relation is declared
The worker SHALL NOT declare a `pg-database` relation, or any other
`postgresql_client` requirer. The worker never talks to PostgreSQL through its
own relation: database host, port, user, name, and password all arrive from the
server over `authentik-cluster`, which is why both charms resolve the same
database. Declaring a second `postgresql_client` requirer would create a
competing database request and break that cohesion.

#### Scenario: No postgresql_client requirer exists
- **WHEN** `charmcraft.yaml` is parsed
- **THEN** `requires` contains no `pg-database` key
- **THEN** no entry under `requires` declares interface `postgresql_client`

### Requirement: Observability endpoints are declared
The `charmcraft.yaml` SHALL declare `metrics-endpoint` with interface
`prometheus_scrape` and `grafana-dashboard` with interface `grafana_dashboard`
under `provides`, and `logging` with interface `loki_push_api` and `tracing`
with interface `tracing` under `requires`. All four SHALL be `optional: true`,
and `tracing` SHALL set `limit: 1`.

#### Scenario: Observability endpoints are present
- **WHEN** `charmcraft.yaml` is parsed
- **THEN** `provides.metrics-endpoint.interface` equals `prometheus_scrape`
- **THEN** `provides.grafana-dashboard.interface` equals `grafana_dashboard`
- **THEN** `requires.logging.interface` equals `loki_push_api`
- **THEN** `requires.tracing.interface` equals `tracing` and `requires.tracing.limit` is `1`

### Requirement: Container runs as the rock's non-root user
The `authentik` container definition SHALL declare `uid: 584792` and
`gid: 584792`, matching the non-root user baked into the authentik-server rock,
and the top-level `charm-user: non-root` setting SHALL be present so the charm
code itself also runs unprivileged.

#### Scenario: Non-root execution is declared
- **WHEN** `charmcraft.yaml` is parsed
- **THEN** the `authentik` container entry declares `uid` equal to `584792`
- **THEN** the `authentik` container entry declares `gid` equal to `584792`
- **THEN** the top-level `charm-user` equals `non-root`

