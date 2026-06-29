## ADDED Requirements

### Requirement: Pebble layer uses startup disabled
The Pebble layer in `PebbleService` SHALL set `"startup": "disabled"` for the worker service so that the service is not started automatically when the layer is applied. The `plan()` method is responsible for starting the service.

#### Scenario: Layer applied with startup disabled
- **WHEN** `PebbleService.plan(layer)` is called
- **THEN** the layer has `startup: disabled` and the service is started explicitly by `plan()`

### Requirement: Pebble layer includes HTTP health check
The Pebble layer SHALL include a health check named `PEBBLE_READY_CHECK_NAME` (`"ready"`) at level `"alive"` using an HTTP check against `http://localhost:9000/-/health/live/`.

#### Scenario: Health check defined in layer
- **WHEN** `PebbleService.render_pebble_layer()` is called
- **THEN** the returned layer contains a check named `"ready"` with `level: alive` and `http.url: http://localhost:9000/-/health/live/`

### Requirement: PebbleService.plan starts service if not running
The `plan()` method SHALL call `self._container.start(SERVICE_NAME)` if the service is not currently running, and `self._container.replan()` if it is already running.

#### Scenario: Service not running
- **WHEN** `plan()` is called and the service is not running
- **THEN** `self._container.start(SERVICE_NAME)` is called

#### Scenario: Service already running
- **WHEN** `plan()` is called and the service is running
- **THEN** `self._container.replan()` is called

#### Scenario: Start raises exception
- **WHEN** starting the service raises an exception
- **THEN** a `PebbleError` is raised with a descriptive message

### Requirement: charm handles pebble_ready event
The charm SHALL observe the `authentik_pebble_ready` event and handle it in a dedicated `_on_pebble_ready` method that: (1) calls `WorkloadService.open_port()`, (2) calls `_on_holistic_handler(event)`, (3) calls `WorkloadService.set_version()`.

#### Scenario: Pebble ready
- **WHEN** the `pebble_ready` event fires for the authentik container
- **THEN** the TCP port is opened, the holistic handler runs, and the workload version is set

### Requirement: charm handles pebble_check_failed event
The charm SHALL observe `authentik_pebble_check_failed` and log a WARNING if the failed check name matches `PEBBLE_READY_CHECK_NAME`.

#### Scenario: Ready check fails
- **WHEN** the `pebble_check_failed` event fires with check name `"ready"`
- **THEN** a WARNING is logged indicating the readiness check failed

#### Scenario: Other check fails
- **WHEN** the `pebble_check_failed` event fires with a different check name
- **THEN** no action is taken

### Requirement: charm handles pebble_check_recovered event
The charm SHALL observe `authentik_pebble_check_recovered` and log an INFO message if the recovered check name matches `PEBBLE_READY_CHECK_NAME`.

#### Scenario: Ready check recovers
- **WHEN** the `pebble_check_recovered` event fires with check name `"ready"`
- **THEN** an INFO is logged indicating the readiness check recovered

### Requirement: charm handles database relation broken
The charm SHALL observe `relation_broken` on the `DATABASE_RELATION` endpoint and stop the workload service if the container is reachable.

#### Scenario: Database relation broken and container reachable
- **WHEN** the `pg-database` `relation_broken` event fires and the container can connect
- **THEN** `self._container.stop(SERVICE_NAME)` is called

#### Scenario: Database relation broken and container not reachable
- **WHEN** the `pg-database` `relation_broken` event fires and the container cannot connect
- **THEN** no stop action is attempted

### Requirement: collect_status reports service health
The `_on_collect_status` handler SHALL add `BlockedStatus("failed to start service, check container logs")` if the container is reachable and `WorkloadService.is_failing()` is `True`, and `WaitingStatus("waiting for service to start")` if the container is reachable and `WorkloadService.is_running()` is `False` (and the service is not failing).

#### Scenario: Service failing
- **WHEN** container is reachable and `WorkloadService.is_failing()` returns `True`
- **THEN** `BlockedStatus("failed to start service, check container logs")` is added

#### Scenario: Service not yet running
- **WHEN** container is reachable and `WorkloadService.is_running()` returns `False` and `is_failing()` returns `False`
- **THEN** `WaitingStatus("waiting for service to start")` is added

#### Scenario: Service running and healthy
- **WHEN** container is reachable and `WorkloadService.is_running()` returns `True`
- **THEN** no waiting/blocked status is added for the service

### Requirement: holistic handler guarded by NOOP_CONDITIONS
The `_holistic_handler()` method SHALL return early without taking any action if any condition in `NOOP_CONDITIONS` returns `False`.

#### Scenario: All NOOP_CONDITIONS met
- **WHEN** all conditions in `NOOP_CONDITIONS` return `True`
- **THEN** the handler proceeds to apply the Pebble layer

#### Scenario: One NOOP_CONDITION not met
- **WHEN** at least one condition in `NOOP_CONDITIONS` returns `False`
- **THEN** the handler returns immediately without calling `PebbleService.plan()`
