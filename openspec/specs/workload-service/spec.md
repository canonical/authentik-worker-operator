# workload-service Specification

## Purpose
TBD - created by archiving change authentik-worker-structural-alignment. Update Purpose after archive.
## Requirements
### Requirement: WorkloadService reports workload version
The `WorkloadService` class in `src/services.py` SHALL expose a `version` property that returns the workload version string obtained by running `ak version` via Pebble exec. If the command fails for any reason, an empty string SHALL be returned.

#### Scenario: Version command succeeds
- **WHEN** `ak version` is executed successfully via Pebble exec
- **THEN** `WorkloadService.version` returns the stripped stdout output

#### Scenario: Version command fails
- **WHEN** `ak version` raises an exception (e.g., Pebble not yet ready)
- **THEN** `WorkloadService.version` returns `""`

### Requirement: WorkloadService sets unit workload version
The `set_version()` method SHALL call `self._unit.set_workload_version(self.version)`. Errors SHALL be logged but not re-raised.

#### Scenario: Version set successfully
- **WHEN** `set_version()` is called and `self._unit.set_workload_version()` succeeds
- **THEN** the unit workload version is set to the value returned by `self.version`

#### Scenario: Version set fails
- **WHEN** `set_version()` is called and `self._unit.set_workload_version()` raises an exception
- **THEN** the error is logged at ERROR level and no exception propagates

### Requirement: WorkloadService opens metrics TCP port
The `open_port()` method SHALL call `self._unit.open_port(protocol="tcp", port=HTTP_PORT)` to open the metrics port.

#### Scenario: Port opened
- **WHEN** `open_port()` is called
- **THEN** `self._unit.open_port(protocol="tcp", port=HTTP_PORT)` is invoked

### Requirement: WorkloadService.is_running checks service and health check
The `is_running()` method SHALL return `True` if and only if: the workload service is in a running state AND the `PEBBLE_READY_CHECK_NAME` health check is in `UP` status.

#### Scenario: Service running and check UP
- **WHEN** the Pebble service is running and the `ready` check status is `UP`
- **THEN** `WorkloadService.is_running()` returns `True`

#### Scenario: Service running but check DOWN
- **WHEN** the Pebble service is running but the `ready` check status is `DOWN`
- **THEN** `WorkloadService.is_running()` returns `False`

#### Scenario: Service not running
- **WHEN** the Pebble service is not running
- **THEN** `WorkloadService.is_running()` returns `False`

#### Scenario: Service fetch fails
- **WHEN** `get_service()` raises `ModelError` or `ConnectionError`
- **THEN** `WorkloadService.is_running()` returns `False` and logs the error

### Requirement: WorkloadService.is_failing checks service and health check
The `is_failing()` method SHALL return `True` if and only if: the workload service is in a running state AND the `PEBBLE_READY_CHECK_NAME` health check is in `DOWN` status.

#### Scenario: Service running and check DOWN
- **WHEN** the Pebble service is running and the `ready` check status is `DOWN`
- **THEN** `WorkloadService.is_failing()` returns `True`

#### Scenario: Service running and check UP
- **WHEN** the Pebble service is running and the `ready` check status is `UP`
- **THEN** `WorkloadService.is_failing()` returns `False`

#### Scenario: Service not running
- **WHEN** the Pebble service is not running
- **THEN** `WorkloadService.is_failing()` returns `False`

#### Scenario: Service fetch fails
- **WHEN** `get_service()` raises `ModelError` or `ConnectionError`
- **THEN** `WorkloadService.is_failing()` returns `False`

