## 1. charmcraft.yaml Fixes

- [x] 1.1 Rename container key from `authentik-worker` to `authentik` in `charmcraft.yaml`
- [x] 1.2 Update `resources.oci-image.upstream-source` to `ghcr.io/goauthentik/server:2026.2.2` in `charmcraft.yaml`
- [x] 1.3 Add `authentik-cluster` entry under `requires` (interface `authentik_cluster`, optional: true) in `charmcraft.yaml`
- [x] 1.4 Add `pg-database` entry under `requires` (interface `postgresql_client`, optional: false, limit: 1) in `charmcraft.yaml`
- [x] 1.5 Remove `uid` and `gid` fields from the `authentik` container spec in `charmcraft.yaml`

## 2. authentik_cluster Library Replacement

- [x] 2.1 Rename `ClusterChangedEvent` and `ClusterRemovedEvent` classes to `AuthentikClusterRequirerReadyEvent` in `lib/charms/authentik_server/v0/authentik_cluster.py`
- [x] 2.2 Replace `AuthentikClusterRequirerEvents` fields (`cluster_changed`, `cluster_removed`) with a single `ready = EventSource(AuthentikClusterRequirerReadyEvent)` in `lib/charms/authentik_server/v0/authentik_cluster.py`
- [x] 2.3 Update `AuthentikClusterRequirer._on_relation_changed` to emit `on.ready` only when `secret_key_secret_id` is present in the databag; remove `_on_relation_broken` in `lib/charms/authentik_server/v0/authentik_cluster.py`
- [x] 2.4 Convert `AuthentikClusterRequirer.is_ready` from a method to a `@property` that checks `secret_key_secret_id` in the databag in `lib/charms/authentik_server/v0/authentik_cluster.py`
- [x] 2.5 Fix `AuthentikClusterProvider.set_secret_key` to look up the existing secret by label `"authentik-secret-key"` (via `model.get_secret(label=...)`) before creating a new one; remove the in-memory `self._secret` field in `lib/charms/authentik_server/v0/authentik_cluster.py`
- [x] 2.6 Bump `LIBPATCH` from 2 to 3 in `lib/charms/authentik_server/v0/authentik_cluster.py`

## 3. charm.py Event Wiring and Handler Rename

- [x] 3.1 Replace `self.framework.observe(self.cluster.on.cluster_changed, self._on_event)` with `self.framework.observe(self.cluster.on.ready, self._on_holistic_handler)` in `src/charm.py`
- [x] 3.2 Remove `self.framework.observe(self.cluster.on.cluster_removed, self._on_event)` from `src/charm.py`
- [x] 3.3 Rename all `self._on_event` references in `framework.observe` calls to `self._on_holistic_handler` in `src/charm.py`
- [x] 3.4 Rename the `_on_event` method to `_on_holistic_handler`; it SHALL set `self.unit.status = ops.MaintenanceStatus("Configuring resources")` before calling `self._reconcile()` in `src/charm.py`

## 4. _on_collect_status Logic Fix

- [x] 4.1 Remove the duplicate `if not self.model.get_relation(CLUSTER_RELATION)` block (second occurrence) from `src/charm.py`
- [x] 4.2 Replace the two separate cluster checks with a single `if/elif` block: `if not self.model.get_relation(CLUSTER_RELATION): event.add_status(BlockedStatus(...))` / `elif not self._cluster_integration.is_ready(): event.add_status(WaitingStatus(...))` in `src/charm.py`
- [x] 4.3 Remove all `return` statements from `_on_collect_status` — statuses accumulate; the ops framework selects the worst automatically in `src/charm.py`

## 5. Unit Tests

- [x] 5.1 Add unit tests for `_on_collect_status` covering the status accumulation paths: pebble not ready, db not ready, cluster relation absent, cluster data not ready, and all-ready → active in `tests/unit/test_charm.py` (note: no early returns; multiple statuses can be added in a single invocation)
- [x] 5.2 Add unit tests for `AuthentikClusterRequirer`: `on.ready` emitted only when `secret_key_secret_id` present, `is_ready` property True/False cases, `get_secret_key()` returns value or None in `tests/unit/test_authentik_cluster.py`
- [x] 5.3 Run `tox -e unit` and confirm all tests pass

## 6. Lint and Format

- [x] 6.1 Run `tox -e fmt` to apply isort and ruff formatting
- [x] 6.2 Run `tox -e lint` and resolve any issues
