## Context

The authentik-worker charm was authored in a hackathon with three categories of defects that
prevent it from being deployed or operating correctly:

1. **`charmcraft.yaml` misconfiguration** — the container name does not match the constant
   used in code, the OCI image reference points to a non-existent registry path, two required
   relations are undeclared, and the container carries `uid`/`gid` fields that conflict with
   the platform-standard `charm-user: non-root` mechanism.

2. **`_on_collect_status` logic bug** — all status checks fall through to `ActiveStatus()`
   because there are no `return` statements after blocking/waiting statuses. Additionally the
   `CLUSTER_RELATION` existence check is copy-pasted twice.

3. **Outdated `authentik_cluster` library** — the `AuthentikClusterRequirer` emits
   `cluster_changed`/`cluster_removed` events that will be replaced by a single `ready` event
   in the canonical upstream library (published by the server charm). The provider side also
   has a secret persistence bug: it stores the secret handle in an instance variable that is
   re-created on every hook invocation, causing `set_secret_key` to create a new secret on
   every call instead of updating the existing one.

4. **Event handler naming** — `_on_event` does not match the canonical `_on_holistic_handler`
   name used in the authentik-server and tenant-service charms, making cross-charm code
   maintenance harder.

## Goals / Non-Goals

**Goals:**
- Make `charmcraft.yaml` deployable with correct container name, image, and relations
- Make `_on_collect_status` correctly reflect unit state using the status accumulation pattern
- Align the bundled `authentik_cluster` lib with the fixed upstream API
- Remove all deprecated event observations from `charm.py`
- Align event handler name with authentik-server / tenant-service (`_on_holistic_handler`)

**Non-Goals:**
- No observability wiring (separate change)
- No changes to `services.py`, `integrations.py`, `configs.py`, or `env_vars.py`
- No new features

## Decisions

### D1: Fix `charmcraft.yaml` in-place, no schema version bump
**Decision**: Edit the existing `charmcraft.yaml` directly.
**Rationale**: All changes are corrections to existing fields or additions of missing fields.
No backwards-incompatible schema change is required.
**Alternative considered**: Extract a Jinja template for env-specific overrides — rejected as
over-engineering for a bug fix.

### D2: Replace lib file wholesale, bump LIBPATCH
**Decision**: Rewrite `lib/charms/authentik_server/v0/authentik_cluster.py` entirely and
increment `LIBPATCH` from 2 to 3.
**Rationale**: The event API change (`cluster_changed` → `ready`) is a breaking change for
consumers. A full replacement is cleaner than a patch diff and matches how `charmcraft` would
publish the updated library.
**Alternative considered**: Keep backward-compatible aliases for old events — rejected because
the only consumer is this charm, and aliases would leave dead code.

### D3: Fix provider secret persistence via label lookup
**Decision**: In `AuthentikClusterProvider.set_secret_key`, attempt to retrieve the secret by
label `"authentik-secret-key"` before deciding to create vs update.
**Rationale**: Juju secrets created with a label can be retrieved by that label in subsequent
hook invocations. Storing a handle in `self._secret` is unreliable because the object is
re-instantiated on every hook.
**Alternative considered**: Store secret id in the unit/app databag — valid but more complex;
label lookup is idiomatic and self-contained within the library.

### D4: Status accumulation — no early returns in `_on_collect_status`
**Decision**: Replace the fall-through status checks with a clean accumulation pattern that adds
all relevant statuses without `return` statements. Use `elif` for the cluster data-readiness
check to avoid calling `is_ready()` on a non-existent relation.
**Rationale**: The `collect-unit-status` hook accumulates statuses; the ops framework selects
the worst automatically. This is the canonical pattern used by authentik-server and
tenant-service — early returns are a divergence that creates unnecessary maintenance overhead.
**Alternative considered**: Early-return pattern — valid logically but diverges from the
platform pattern and is harder to extend with additional checks (e.g. `is_running/is_failing`
added in the structural-alignment change).

### D5: Rename `_on_event` → `_on_holistic_handler`
**Decision**: Rename the generic `_on_event` dispatch method to `_on_holistic_handler`, and
have it set `MaintenanceStatus` before delegating to `_reconcile()`.
**Rationale**: `_on_holistic_handler` is the canonical name across authentik-server and
tenant-service. Consistent naming reduces cognitive load when reading or porting code.
**Alternative considered**: Keep `_on_event` — rejected to avoid cross-charm inconsistency.

## Risks / Trade-offs

- **[Risk] LIBPATCH bump is cosmetic without charmcraft publish** — the local copy is updated
  but the Charmhub-hosted library remains at LIBPATCH=2 until a maintainer runs
  `charmcraft publish-lib`. Mitigation: document in PR description that the lib must be
  re-published after merge.

- **[Risk] Removing `cluster_removed` observation** — the charm no longer explicitly handles
  the broken-relation event. Mitigation: `_reconcile()` is holistic and driven by
  `collect-unit-status`; when the relation is removed Juju will fire `collect-unit-status`
  and the status handler will correctly report `BlockedStatus`. No deferred state is left
  behind.

## Migration Plan

All changes are in-place edits to existing files. No database migration, relation migration,
or peer-relation data migration is needed. Deploying a newly-packed charm over an existing
unit will trigger `config-changed` → `_reconcile()`, which will re-evaluate the corrected
conditions.

## Open Questions

- None — all decisions are unambiguous given the constraints.
