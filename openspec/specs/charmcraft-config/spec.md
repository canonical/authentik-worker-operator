# charmcraft-config Specification

## Purpose
TBD - created by archiving change authentik-worker-core-fixes. Update Purpose after archive.
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
The `oci-image` resource `upstream-source` SHALL be set to `ghcr.io/goauthentik/server:2026.2.2`.
The worker uses the same container image as the server, launched with the `ak worker` command.

#### Scenario: Image reference is correct
- **WHEN** `charmcraft.yaml` is parsed
- **THEN** `resources.oci-image.upstream-source` equals `ghcr.io/goauthentik/server:2026.2.2`

### Requirement: authentik-cluster relation is declared
The `charmcraft.yaml` SHALL declare an `authentik-cluster` relation under `requires` with
interface `authentik_cluster` and `optional: true`.

#### Scenario: Relation is present
- **WHEN** `charmcraft.yaml` is parsed
- **THEN** `requires.authentik-cluster.interface` equals `authentik_cluster`
- **THEN** `requires.authentik-cluster.optional` is `true`

### Requirement: pg-database relation is declared
The `charmcraft.yaml` SHALL declare a `pg-database` relation under `requires` with
interface `postgresql_client`, `optional: false`, and `limit: 1`.

#### Scenario: Relation is present
- **WHEN** `charmcraft.yaml` is parsed
- **THEN** `requires.pg-database.interface` equals `postgresql_client`
- **THEN** `requires.pg-database.optional` is `false`

### Requirement: Container spec has no uid/gid fields
The container definition in `charmcraft.yaml` SHALL NOT contain `uid` or `gid` fields.
Non-root execution is managed by the top-level `charm-user: non-root` setting.

#### Scenario: No uid/gid in container spec
- **WHEN** `charmcraft.yaml` is parsed
- **THEN** the `authentik` container entry does not contain a `uid` field
- **THEN** the `authentik` container entry does not contain a `gid` field

