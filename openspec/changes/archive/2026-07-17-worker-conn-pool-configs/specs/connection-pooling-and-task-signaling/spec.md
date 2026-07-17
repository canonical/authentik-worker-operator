## ADDED Requirements

### Requirement: Declare connection pooling and timeout configurations in Juju
The `charmcraft.yaml` config section SHALL declare four new configuration options:
- `postgresql_disable_server_side_cursors` (boolean, default false)
- `postgresql_conn_health_checks` (boolean, default false)
- `postgresql_conn_max_age` (integer, default 0)
- `consumer_listen_timeout` (integer, default 30)

#### Scenario: Verify Juju config option declarations
- **WHEN** `charmcraft.yaml` is parsed
- **THEN** the config options contain `postgresql_disable_server_side_cursors` with default `false`
- **THEN** the config options contain `postgresql_conn_health_checks` with default `false`
- **THEN** the config options contain `postgresql_conn_max_age` with default `0`
- **THEN** the config options contain `consumer_listen_timeout` with default `30`

### Requirement: Default worker environment has standard values
The `DEFAULT_WORKER_ENV` dictionary in `src/env_vars.py` SHALL define standard default values for the connection-pooling and consumer timeout configurations:
- `AUTHENTIK_POSTGRESQL__DISABLE_SERVER_SIDE_CURSORS` is `"false"`
- `AUTHENTIK_POSTGRESQL__CONN_HEALTH_CHECKS` is `"false"`
- `AUTHENTIK_POSTGRESQL__CONN_MAX_AGE` is `"0"`
- `AUTHENTIK_WORKER__CONSUMER_LISTEN_TIMEOUT` is `"30"`

#### Scenario: Default environment check
- **WHEN** `DEFAULT_WORKER_ENV` is accessed
- **THEN** `AUTHENTIK_POSTGRESQL__DISABLE_SERVER_SIDE_CURSORS` equals `"false"`
- **THEN** `AUTHENTIK_POSTGRESQL__CONN_HEALTH_CHECKS` equals `"false"`
- **THEN** `AUTHENTIK_POSTGRESQL__CONN_MAX_AGE` equals `"0"`
- **THEN** `AUTHENTIK_WORKER__CONSUMER_LISTEN_TIMEOUT` equals `"30"`

### Requirement: CharmConfig maps config to environment variables
The `CharmConfig.to_env_vars()` method SHALL read the four new configuration options from Juju config, convert booleans to lowercase string representations (`"true"` or `"false"`), and map them to their corresponding environment variables:
- `postgresql_disable_server_side_cursors` -> `AUTHENTIK_POSTGRESQL__DISABLE_SERVER_SIDE_CURSORS`
- `postgresql_conn_health_checks` -> `AUTHENTIK_POSTGRESQL__CONN_HEALTH_CHECKS`
- `postgresql_conn_max_age` -> `AUTHENTIK_POSTGRESQL__CONN_MAX_AGE`
- `consumer_listen_timeout` -> `AUTHENTIK_WORKER__CONSUMER_LISTEN_TIMEOUT`

#### Scenario: Custom connection pool and timeout config mapped
- **WHEN** Juju config has `postgresql_disable_server_side_cursors = true`, `postgresql_conn_health_checks = true`, `postgresql_conn_max_age = 10`, `consumer_listen_timeout = 5`
- **THEN** `to_env_vars()` returns a dictionary containing:
  - `AUTHENTIK_POSTGRESQL__DISABLE_SERVER_SIDE_CURSORS` equal to `"true"`
  - `AUTHENTIK_POSTGRESQL__CONN_HEALTH_CHECKS` equal to `"true"`
  - `AUTHENTIK_POSTGRESQL__CONN_MAX_AGE` equal to `"10"`
  - `AUTHENTIK_WORKER__CONSUMER_LISTEN_TIMEOUT` equal to `"5"`
