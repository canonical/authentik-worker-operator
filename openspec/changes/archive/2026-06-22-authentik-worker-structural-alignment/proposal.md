## Why

The authentik-worker charm's source structure has diverged from the authentik-server and tenant-service charms, making cross-charm maintenance harder and leaving known gaps: no `utils.py` with NOOP_CONDITIONS, no `WorkloadService` abstraction, incorrect Pebble `startup: "enabled"`, and a class-based `DatabaseIntegration` instead of a frozen dataclass. Aligning the structure now reduces cognitive overhead and prevents bug classes already solved in the sibling charms.

## What Changes

- `src/constants.py` — add `PEBBLE_READY_CHECK_NAME`, `WORKLOAD_SERVICE`, `HTTP_PORT`
- `src/services.py` — add `WorkloadService` class; fix `PebbleService`: `startup: "disabled"`, proper health check, correct restart logic
- `src/integrations.py` — replace `DatabaseIntegration` class with `DatabaseConfig` frozen dataclass (`@dataclass(frozen=True)`) with `load()` classmethod
- `src/configs.py` — add `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY` env vars
- `src/utils.py` (new) — `container_connectivity`, `database_integration_exists`, `database_resource_is_created`, `cluster_integration_exists`, `NOOP_CONDITIONS` tuple
- `src/charm.py` — import and use `WorkloadService`, `DatabaseConfig`, `NOOP_CONDITIONS`; add `_on_pebble_ready`, `_on_pebble_check_failed`, `_on_pebble_check_recovered`, `_on_database_integration_broken`; add service health checks to `_on_collect_status`

## Capabilities

### New Capabilities

- `utils`: `utils.py` module with NOOP_CONDITIONS tuple and condition factory functions
- `workload-service`: `WorkloadService` class in `services.py` (version, set_version, open_port, is_running, is_failing)
- `pebble-lifecycle`: Pebble layer startup fix, HTTP health check, restart logic, `_on_pebble_ready/check_failed/recovered`, `_on_database_integration_broken`
- `database-config-dataclass`: `DatabaseConfig` frozen dataclass replacing `DatabaseIntegration`
- `proxy-config`: proxy env vars (`HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`) in `configs.py`

### Modified Capabilities

<!-- No existing spec-level requirements are changing -->

## Non-goals

- No observability wiring (separate `authentik-worker-observability` change)
- No authentik_cluster library changes (separate `authentik-worker-core-fixes` change)
- No charmcraft.yaml changes
- No test writing (separate `authentik-worker-tests` change)
- No KubernetesComputeResourcesPatch wiring

## Impact

- `src/utils.py` — new file
- `src/constants.py` — three new constants
- `src/services.py` — new `WorkloadService` class; `PebbleService` layer and `plan()` fixes
- `src/integrations.py` — `DatabaseConfig` dataclass (replaces `DatabaseIntegration`); `AuthentikClusterIntegration` unchanged
- `src/configs.py` — three new proxy env vars
- `src/charm.py` — updated imports, new handlers, NOOP_CONDITIONS guard, collect_status improvements
