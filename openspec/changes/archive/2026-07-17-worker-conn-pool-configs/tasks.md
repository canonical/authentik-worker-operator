## 1. Declare Configurations

- [x] 1.1 Add the new Juju config options in `charmcraft.yaml`.

## 2. Register Default Environment Variables

- [x] 2.1 Add the connection pool and consumer timeout default variables to `DEFAULT_WORKER_ENV` in `src/env_vars.py`.

## 3. Map Configs to Environment Variables

- [x] 3.1 Modify `CharmConfig.to_env_vars()` in `src/configs.py` to parse and map the new config options to environment variables.

## 4. Quality and Validation

- [x] 4.1 Update worker unit tests in the `tests/` directory to verify config options map correctly to Pebble layer environment variables.
- [x] 4.2 Run formatting, linting, and unit tests via `tox -e fmt && tox -e lint && tox -e unit`.
