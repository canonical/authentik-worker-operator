## ADDED Requirements

### Requirement: collect_status uses status accumulation without early returns
`_on_collect_status` in `charm.py` SHALL add all relevant statuses via `event.add_status()`
without early returns. The ops framework selects the "worst" status automatically (Blocked >
Waiting > Maintenance > Active). This mirrors the tenant-service and authentik-server pattern.

#### Scenario: Pebble not ready adds waiting status
- **WHEN** `_on_collect_status` fires and the container cannot connect
- **THEN** `WaitingStatus("waiting for pebble")` is added
- **THEN** remaining checks continue (they may also add statuses)

#### Scenario: Missing database relation adds blocked status
- **WHEN** `_on_collect_status` fires and the database integration is not ready
- **THEN** `BlockedStatus("missing pg-database relation")` is added
- **THEN** other checks also run and may add their own statuses

#### Scenario: Missing cluster relation adds blocked status
- **WHEN** `_on_collect_status` fires and no `authentik-cluster` relation exists
- **THEN** `BlockedStatus("missing authentik-cluster relation")` is added

#### Scenario: Cluster data not yet available adds waiting status
- **WHEN** `_on_collect_status` fires, the cluster relation exists but data is not ready
- **THEN** `WaitingStatus("waiting for authentik-cluster data")` is added

#### Scenario: All preconditions met sets active
- **WHEN** `_on_collect_status` fires and all integrations are ready
- **THEN** `ActiveStatus()` is added as the final status

### Requirement: No duplicate relation checks
`_on_collect_status` SHALL check `CLUSTER_RELATION` existence exactly once, using `elif` to
guard the `is_ready()` call so it is not invoked when the relation is absent.

#### Scenario: Single cluster-relation check
- **WHEN** `_on_collect_status` is inspected statically
- **THEN** `self.model.get_relation(CLUSTER_RELATION)` appears exactly once
- **THEN** `elif not self._cluster_integration.is_ready()` is used for the data-not-ready check
