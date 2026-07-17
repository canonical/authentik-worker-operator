## Why

The Authentik worker operator communicates with PostgreSQL and needs configuration options for PgBouncer transaction-level connection pooling compatibility, specifically cursor disabling, connectivity health checks, and connection maximum age limits, to align with the server charm. Additionally, because transaction pooling does not support PostgreSQL's `LISTEN/NOTIFY` mechanism, the worker requires adjustable listener polling timeouts to reduce background task latency from the default thirty seconds.

## What Changes

- Add three PgBouncer connection tuning configurations and one consumer listen timeout configuration to `charmcraft.yaml`.
- Register the default values for the corresponding environment variables in `src/env_vars.py`.
- Map the config options to environment variables inside `CharmConfig.to_env_vars` in `src/configs.py`.
- Add unit tests in the `tests/` directory to verify configurations map onto Pebble layer environment variables.

## Capabilities

### New Capabilities
- `connection-pooling-and-task-signaling`: Expose configurations for PgBouncer integration (cursor disabling, health checks, max connection age) and adjustable worker consumer listen timeouts.

### Modified Capabilities

## Non-goals

- Altering the PostgreSQL relation interfaces or database schema.
- Implementing automatic PgBouncer detection or dynamic pooling logic inside the workload.
- Managing database server configurations or deploying a PgBouncer service inside the operator.

## Impact

- **Configuration changes**: `charmcraft.yaml` gains `postgresql_disable_server_side_cursors`, `postgresql_conn_health_checks`, `postgresql_conn_max_age`, and `consumer_listen_timeout` options.
- **Affected source files**: `src/configs.py`, `src/env_vars.py`.
- **Testing**: Test cases in the `tests/unit/` suite will be updated.
