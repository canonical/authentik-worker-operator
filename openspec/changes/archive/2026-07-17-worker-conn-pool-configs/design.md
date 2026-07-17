## Context

When utilizing transaction-level connection pooling (e.g., PgBouncer or Pgpool) for PostgreSQL, certain core database operations break. In particular, server-side cursors will fail across different pooled connections. To support transaction pooling compatibility, PgBouncer requires configurations such as cursor disabling, connection health checks, and maximum connection age constraints. 
Additionally, PgBouncer's transaction pooling mode does not support PostgreSQL's `LISTEN/NOTIFY` system. In this setup, the Authentik worker falls back to checking the database periodically (polling). By default, this listener timeout is set to 30 seconds, causing long processing delays. Providing a Juju configuration to reduce this listener timeout helps avoid latency.

## Goals / Non-Goals

**Goals:**
- Expose four Juju configurations to manage connection pooling compatibility and polling fallback timeouts in `charmcraft.yaml`.
- Ensure default values in `src/env_vars.py` match standard, safe default expectations.
- Safely parse and convert boolean configurations to lowercase strings within `CharmConfig.to_env_vars()` inside `src/configs.py`.
- Verify the environment variable mappings are covered by the unit testing suite in `tests/`.

**Non-Goals:**
- Changing how the worker relates to or registers with the database.
- Writing code to perform connection pooling inside the Python operator itself.

## Decisions

- **Decision 1: Use string representations of booleans for environment variables**
  - *Rationale*: Environment variables passed down to the Pebble container must be strings. Hence, `True` and `False` values from the Juju config options are explicitly converted to `"true"` and `"false"` (using lowercase as expected by the Authentik application).
  - *Alternatives considered*: Passing Python `bool` types, which might cause Pebble validation or serialization errors.

- **Decision 2: Maintain default settings as non-disabling / standard defaults**
  - *Rationale*: Out-of-the-box, connection pooling is disabled (i.e. cursors are enabled, no health checks, no connection age limit) and the polling listen timeout remains 30s. This preserves existing behavior when pooling is not used.
  - *Alternatives considered*: Forcing lower values for consumer timeout by default. This is rejected to match the standard upstream Authentik defaults.

## Risks / Trade-offs

- **Risk**: Overly low `consumer_listen_timeout` might cause high CPU/DB poll rates.
  - *Mitigation*: The default is left at 30 seconds, and users can consciously tune the configuration option based on their cluster workload limits.
