---
description: "Use when writing or modifying unit tests, integration tests, test fixtures, or conftest files for the charm. Covers test file structure, create_state() factory, ops.testing (Scenario) usage, and test organization."
applyTo: "tests/**"
---

# Testing Guidelines

## File Structure

One file per concern:

| File | Scope |
|------|-------|
| `test_charm.py` | Lifecycle events, `_reconcile()`, collect-status, relation events |
| `test_integrations.py` | Integration wrapper classes tested in isolation |
| `test_configs.py` | `CharmConfig` validation and env var output |

**Do NOT** add test files for `lib/charms/` libraries owned by other repos (e.g. `authentik_cluster` is owned by `authentik-server`).

## Unit Tests (`tests/unit/`)

- **Framework**: `ops.testing` (Scenario). Do not use legacy `Harness`.
- **State factory**: Use `create_state()` — a **module-level factory function** in `conftest.py` (NOT a fixture). Import it directly in test files.
- **Do NOT** use `dataclasses.replace()` to modify states. Always create a fresh state via `create_state()`.
- Group tests in classes by event or feature (e.g., `TestPebbleReadyEvent`, `TestCollectStatusEvent`).
- **No inline imports** — all imports must be at the top of the file.

### `create_state()` Factory Pattern

```python
from unit.conftest import create_state

# Minimal state (leader=True, can_connect=True, no relations)
state = create_state()

# Custom state
state = create_state(
    leader=False,
    relations=[db_relation, cluster_relation],
    config={"log_level": "debug"},
    can_connect=False,
)
```

Supported kwargs: `leader`, `secrets`, `relations`, `containers`, `config`, `can_connect`.
The factory builds a `testing.State` with a bare container (no pre-baked Pebble layers). Layers are produced by the charm's reconciliation, not baked into the input state.

### Mocking Rules

Autouse fixtures in `conftest.py` (apply to every test automatically):

- **`mocked_k8s_resource_patch`** — Mocks `KubernetesComputeResourcesPatch` using two fixtures: `mocked_resource_patch` (patches `ResourcePatcher`) + `mocked_k8s_resource_patch` (patches via `mocker.patch.multiple`).

Named fixtures available on demand:

- **`mocked_holistic_handler`** — Replaces `_on_holistic_handler` with a mock; use in event-routing tests to isolate routing from reconciliation logic.
- **`mocked_workload_service_version`** — `PropertyMock` on `WorkloadService.version`; use when testing events that call `set_version()`.
- **`mocked_open_port`** — Mocks `WorkloadService.open_port`; use in `pebble_ready` tests.
- **`mocked_is_running`** / **`mocked_is_failing`** — Mock service health checks.
- Individual condition fixtures: `mocked_container_connectivity`, `mocked_database_integration_exists`, `mocked_database_resource_is_created`, `mocked_cluster_integration_exists`.
- **`all_satisfied_conditions`** — Activates all condition mocks so every guard passes; use in `TestCollectStatusEvent` to isolate individual failures via `patch()`.

Use `create_autospec()` for library objects in integration wrapper tests.

### Integration Wrapper Test Pattern

Test wrappers in isolation using `create_autospec()` for library objects:
- `to_env_vars()`: verify correct env var keys and values
- `is_ready()`: test true/false paths

These are pure mock tests — no `create_state()` needed.

```python
def test_database_integration_env_vars() -> None:
    db = create_autospec(DatabaseRequires)
    db.fetch_relation_data.return_value = {
        1: {"endpoints": "host:5432", "username": "u", "password": "p", "database": "authentik"}
    }
    integration = DatabaseIntegration(db)
    env = integration.to_env_vars()
    assert env["AUTHENTIK_POSTGRESQL__HOST"] == "host"
    assert env["AUTHENTIK_POSTGRESQL__PORT"] == "5432"
```

### Collect-Status Test Pattern

Use `all_satisfied_conditions` + `@pytest.mark.parametrize` to cover all failing condition paths without duplicating state setup:

```python
@pytest.mark.parametrize(
    "condition, condition_value, status, message",
    [("container_connectivity", False, testing.WaitingStatus, "waiting for pebble"), ...],
)
def test_when_condition_fails(self, context, all_satisfied_conditions, condition, ...):
    state = create_state()
    with patch(f"charm.{condition}", return_value=condition_value):
        state_out = context.run(context.on.collect_unit_status(), state)
    assert isinstance(state_out.unit_status, status)
```

## Integration Tests (`tests/integration/`)

- **Framework**: `jubilant` library.
- **Lifecycle order**: deploy → health check → scale up → integrations → scale down → removal.
- **Skippable**: Deploy (`--no-deploy`) and removal (`--keep-models`) must be skippable.
- Use `conftest.py` for model/charm fixtures, `constants.py` for app names, `utils.py` for helpers.
