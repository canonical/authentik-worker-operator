## Why

The charm was authored in a hackathon with intentional shortcuts that prevent it from being
deployed or operated correctly. Three categories of defects must be fixed before the charm
can be considered production-ready: a misconfigured `charmcraft.yaml`, logic bugs in status
reporting, and an outdated charm library that uses a superseded event API.

## What Changes

- Fix container name in `charmcraft.yaml`: `authentik-worker` → `authentik` (aligns with `WORKLOAD_CONTAINER` constant)
- Fix OCI image `upstream-source`: `ghcr.io/canonical/authentik-worker:v0.2.0` (non-existent) → `ghcr.io/goauthentik/server:2026.2.2`
- Add missing `authentik-cluster` relation declaration to `charmcraft.yaml` (requires, interface `authentik_cluster`, optional)
- Remove `gid`/`uid` fields from the container spec in `charmcraft.yaml` (charm runs non-root via `charm-user`)
- Fix `_on_collect_status` in `charm.py`: replace early-return pattern with status accumulation (no `return` after each status); use `elif` to guard the cluster-data check; remove duplicate `CLUSTER_RELATION` check; align with authentik-server / tenant-service pattern
- Rename `_on_event` → `_on_holistic_handler` in `charm.py`; have it set `MaintenanceStatus("Configuring resources")` before delegating to `_reconcile()`
- Replace `lib/charms/authentik_server/v0/authentik_cluster.py` with the fixed version: `AuthentikClusterRequirerEvents` gains `ready` event, drops broken `cluster_changed`/`cluster_removed` events, and the provider fixes the secret persistence bug (in-memory `_secret` field)
- Update `charm.py` to observe `cluster.on.ready` instead of `cluster.on.cluster_changed`; remove observation of `cluster.on.cluster_removed`; rename all `_on_event` observations to `_on_holistic_handler`

## Capabilities

### New Capabilities

- `charmcraft-config`: Correct `charmcraft.yaml` container, OCI image, relations, and non-root container spec
- `collect-status-logic`: Correct `_on_collect_status` accumulation pattern; `elif` cluster-data guard; rename handler to `_on_holistic_handler`
- `authentik-cluster-lib`: Updated `AuthentikClusterRequirer` library with fixed event API and secret persistence

### Modified Capabilities

<!-- None — no existing specs to delta against -->

## Non-goals

- No new features or behaviour changes beyond fixing the identified defects
- No observability wiring (addressed in a separate change)
- No changes to `services.py`, `integrations.py`, `configs.py`, or `env_vars.py`

## Impact

- `charmcraft.yaml` — container name, image, relations, uid/gid
- `src/charm.py` — `_on_collect_status`, event observation for cluster
- `lib/charms/authentik_server/v0/authentik_cluster.py` — full replacement
