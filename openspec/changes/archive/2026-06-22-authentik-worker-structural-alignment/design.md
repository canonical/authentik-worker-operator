## Context

The authentik-worker charm (`src/`) currently diverges from the authentik-server operator and tenant-service operator in several structural ways:

1. **No `utils.py`**: The worker has no NOOP_CONDITIONS guard, so `_reconcile()` manually checks `can_connect`, database readiness, and cluster readiness inline with conditional returns.
2. **No `WorkloadService`**: Version reporting and port management are absent; the worker neither sets the workload version nor opens TCP ports.
3. **`startup: "enabled"` in Pebble layer**: This causes Pebble to start the service automatically even before env vars are provided, which can cause premature startup with missing config.
4. **Class-based `DatabaseIntegration`**: The server and tenant-service charms use `@dataclass(frozen=True)` for database config, making the object immutable and easier to reason about. The worker uses a stateful class that holds a reference to `DatabaseRequires` and fetches data on every call.
5. **No proxy env vars in `configs.py`**: The server charm supports `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY` from charm config; the worker does not.

The reference implementations are:
- `authentik-server-operator/src/utils.py` — NOOP_CONDITIONS pattern
- `authentik-server-operator/src/services.py` — `WorkloadService` + `PebbleService` with restart logic
- `authentik-server-operator/src/integrations.py` — `DatabaseConfig` frozen dataclass with `load()` classmethod

## Goals / Non-Goals

**Goals:**
- Introduce `src/utils.py` with NOOP_CONDITIONS and condition factory functions matching the server charm pattern
- Add `WorkloadService` class to `src/services.py` for version, port, and health state management
- Fix `PebbleService`: set `startup: "disabled"`, add HTTP health check, fix `plan()` to start/replan correctly
- Replace `DatabaseIntegration` with `DatabaseConfig` frozen dataclass in `src/integrations.py`
- Add proxy env vars to `src/configs.py`
- Update `src/charm.py` to use all of the above: NOOP_CONDITIONS guard, `WorkloadService`, `DatabaseConfig.load()`, new pebble/db event handlers, improved `_on_collect_status`
- Add constants `PEBBLE_READY_CHECK_NAME`, `WORKLOAD_SERVICE`, `HTTP_PORT` to `src/constants.py`

**Non-Goals:**
- Observability integration (loki, tracing) — separate `authentik-worker-observability` change
- Changes to `lib/charms/` (managed by charmcraft — read-only)
- charmcraft.yaml changes
- KubernetesComputeResourcesPatch wiring
- Writing or updating tests — separate `authentik-worker-tests` change

## Decisions

### D1: Copy `DatabaseConfig` pattern verbatim from the server charm

**Decision**: Replace `DatabaseIntegration` with a `@dataclass(frozen=True, slots=True)` named `DatabaseConfig`, with a `load(cls, requirer: DatabaseRequires) -> "DatabaseConfig"` classmethod and an `is_ready() -> bool` method.

**Rationale**: Frozen dataclasses are immutable and can be reconstructed cheaply on each reconcile call instead of being stored in `__init__`. This eliminates stale-reference bugs and matches the established pattern. The `load()` classmethod keeps data-fetching logic encapsulated.

**Alternative considered**: Keep class-based approach, add `load()` as a factory method. Rejected because mutable state stored in `__init__` is harder to reason about across reconcile cycles.

### D2: Use `NOOP_CONDITIONS` tuple in `_reconcile()` (renamed `_holistic_handler()`)

**Decision**: Guard `_holistic_handler()` with `if not all(condition(self) for condition in NOOP_CONDITIONS): return`. The NOOP_CONDITIONS tuple contains `container_connectivity`, `database_integration_exists`, `database_resource_is_created`.

**Rationale**: Centralizes all early-exit conditions in one place, matching the server charm pattern. Makes the condition set explicit, inspectable, and testable without reading the body of `_holistic_handler`.

**Note**: `cluster_integration_exists` is NOT included in NOOP_CONDITIONS because the cluster check needs to report a specific blocked status — it should remain in `_on_collect_status`, not silently return from the handler.

### D3: HTTP health check instead of exec health check

**Decision**: Replace the existing `exec`-based `ak healthcheck` check with an HTTP check against `http://localhost:9000/-/health/live/`, named `PEBBLE_READY_CHECK_NAME = "ready"`.

**Rationale**: HTTP checks are more representative of actual service readiness (checks the HTTP listener, not just the process). The server charm uses this pattern. The existing exec check is kept in spirit but replaced for consistency.

### D4: `startup: "disabled"` in Pebble layer

**Decision**: Change `startup` from `"enabled"` to `"disabled"` in `PEBBLE_LAYER_DICT`.

**Rationale**: With `startup: "enabled"`, Pebble starts the service as soon as the layer is added, before env vars (database credentials, secret key) are injected. The `plan()` method must be responsible for starting the service explicitly after the full layer is applied. This matches the server charm and avoids partially-configured startups.

**Consequence**: `PebbleService.plan()` must explicitly call `self._container.start(SERVICE_NAME)` if the service is not running, rather than relying on Pebble's auto-start.

### D5: Separate `_on_pebble_ready` handler

**Decision**: Instead of routing `pebble_ready` to `_on_holistic_handler` directly, add a dedicated `_on_pebble_ready` method that calls `open_port()`, then `_on_holistic_handler(event)`, then `set_version()`.

**Rationale**: Port opening and version setting are one-time pebble-ready concerns. Embedding them in the holistic handler would cause them to run on every reconcile. Matching the server charm's lifecycle pattern.

## Risks / Trade-offs

- **[Risk] `DatabaseConfig.is_ready()` changes semantics slightly**: The old `DatabaseIntegration.is_ready()` returns `bool(self._get_connection())` which checks for a fully populated endpoint. The new `is_ready() -> bool` returns `bool(self.host and self.port and self.username)`. These are equivalent in practice because `load()` populates all fields from the same source.
  → **Mitigation**: The `_on_collect_status` check and NOOP_CONDITIONS both use `database_resource_is_created()` (which calls `self.database.is_resource_created()`), so collect_status independently validates DB readiness.

- **[Risk] Removing `_db_integration` from `__init__`**: `DatabaseConfig` is now constructed in `_holistic_handler()` via `DatabaseConfig.load(self.database)`. Any code path that previously used `self._db_integration` will need updating.
  → **Mitigation**: All usages are in `_reconcile()` → `_holistic_handler()`, so this is a contained change.

- **[Risk] `startup: "disabled"` + explicit `start()`**: If `plan()` is called but the start raises, the error is caught and re-raised as `PebbleError`. Callers in `_holistic_handler` must handle this.
  → **Mitigation**: `_holistic_handler` already handles `PebbleError` via the existing exception flow.

## Migration Plan

This is a charm source-only change. No workload migration is needed. The change takes effect on the next reconcile cycle (e.g., `config-changed`, `pebble-ready`). Rolling upgrade is safe — the pebble layer change (`startup: "disabled"`) only affects newly started services; existing running services are unaffected until `replan()` is called.

## Open Questions

None. All patterns are established in reference charms.
