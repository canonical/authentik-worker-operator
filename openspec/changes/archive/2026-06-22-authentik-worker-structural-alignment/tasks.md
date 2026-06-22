## 1. Constants

- [x] 1.1 Add `PEBBLE_READY_CHECK_NAME = "ready"`, `WORKLOAD_SERVICE = "authentik-worker"`, and `HTTP_PORT: int = 9000` to `src/constants.py`

## 2. Integrations — DatabaseConfig dataclass

- [x] 2.1 Remove `DatabaseIntegration` class from `src/integrations.py`
- [x] 2.2 Add `@dataclass(frozen=True, slots=True)` `DatabaseConfig` with fields `host: str = ""`, `port: str = ""`, `user: str = ""`, `password: str = ""`, `name: str = ""`
- [x] 2.3 Implement `to_env_vars(self) -> EnvVars` on `DatabaseConfig` returning all five `AUTHENTIK_POSTGRESQL__` keys
- [x] 2.4 Implement `is_ready(self) -> bool` returning `bool(self.host and self.port and self.user)`
- [x] 2.5 Implement `load(cls, database: DatabaseRequires) -> "DatabaseConfig"` classmethod that parses `fetch_relation_data()` — returns `cls()` if no relations or no `"endpoints"` key; otherwise parses `host:port` from `endpoints` and constructs `DatabaseConfig` with all fields

## 3. Configs — proxy env vars

- [x] 3.1 Add proxy env var extraction to `CharmConfig.to_env_vars()` in `src/configs.py`: add `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY` from `self._config.get("http_proxy")`, `self._config.get("https_proxy")`, `self._config.get("no_proxy")` — only include each key if the config value is non-None and non-empty

## 4. Services — WorkloadService and PebbleService fixes

- [x] 4.1 Add imports in `src/services.py`: `from ops.pebble import CheckStatus` and update constants import to include `PEBBLE_READY_CHECK_NAME`, `WORKLOAD_SERVICE`, `HTTP_PORT`
- [x] 4.2 Update `PEBBLE_LAYER_DICT` in `src/services.py`: change `"startup"` from `"enabled"` to `"disabled"`; replace the existing `"health"` exec check with `PEBBLE_READY_CHECK_NAME: {"override": "replace", "level": "alive", "http": {"url": "http://localhost:9000/-/health/live/"}}`
- [x] 4.3 Fix `PebbleService.plan()` in `src/services.py`: replace `self._container.replan()` with: if service not running call `self._container.start(SERVICE_NAME)`, else call `self._container.replan()`
- [x] 4.4 Add `WorkloadService` class to `src/services.py` with `__init__(self, unit: Unit)` storing `self._unit` and `self._container = unit.get_container(WORKLOAD_CONTAINER)`
- [x] 4.5 Implement `WorkloadService.version` property: exec `["ak", "version"]`, return stripped stdout; return `""` on any exception
- [x] 4.6 Implement `WorkloadService.set_version(self) -> None`: call `self._unit.set_workload_version(self.version)`; log ERROR on exception, do not re-raise
- [x] 4.7 Implement `WorkloadService.open_port(self) -> None`: call `self._unit.open_port(protocol="tcp", port=HTTP_PORT)`
- [x] 4.8 Implement `WorkloadService.is_running(self) -> bool`: catch `ModelError`/`ConnectionError` on `get_service()` and return `False`; if service not running return `False`; get check by `PEBBLE_READY_CHECK_NAME` and return `True` only if status is `CheckStatus.UP`
- [x] 4.9 Implement `WorkloadService.is_failing(self) -> bool`: catch `ModelError`/`ConnectionError` and return `False`; if service not running return `False`; return `True` only if check status is `CheckStatus.DOWN`

## 5. Utils — new module

- [x] 5.1 Create `src/utils.py` with `TYPE_CHECKING` import of `AuthentikWorkerCharm`
- [x] 5.2 Add `Condition = Callable[["AuthentikWorkerCharm"], bool]` type alias
- [x] 5.3 Implement `container_connectivity(charm) -> bool` — `charm.unit.get_container(WORKLOAD_CONTAINER).can_connect()`
- [x] 5.4 Implement `database_integration_exists(charm) -> bool` — `bool(charm.model.relations[DATABASE_RELATION])`
- [x] 5.5 Implement `database_resource_is_created(charm) -> bool` — `charm.database.is_resource_created()`
- [x] 5.6 Implement `cluster_integration_exists(charm) -> bool` — `bool(charm.model.get_relation(CLUSTER_RELATION))`
- [x] 5.7 Define `NOOP_CONDITIONS: tuple[Condition, ...] = (container_connectivity, database_integration_exists, database_resource_is_created)`

## 6. Charm — wire everything together

- [x] 6.1 Update imports in `src/charm.py`: add `WorkloadService` from `services`; add `DatabaseConfig` (remove `DatabaseIntegration`) from `integrations`; add `NOOP_CONDITIONS`, `container_connectivity`, `database_integration_exists`, `database_resource_is_created`, `cluster_integration_exists` from `utils`
- [x] 6.2 In `AuthentikWorkerCharm.__init__`: add `self._workload_service = WorkloadService(self.unit)`; remove `self._db_integration = DatabaseIntegration(self.database)` (DatabaseConfig is now loaded per-reconcile)
- [x] 6.3 Replace `self.framework.observe(self.on.authentik_pebble_ready, self._on_event)` with `self.framework.observe(self.on.authentik_pebble_ready, self._on_pebble_ready)` in `__init__`
- [x] 6.4 Add `self.framework.observe(self.on.authentik_pebble_check_failed, self._on_pebble_check_failed)` in `__init__`
- [x] 6.5 Add `self.framework.observe(self.on.authentik_pebble_check_recovered, self._on_pebble_check_recovered)` in `__init__`
- [x] 6.6 Add `self.framework.observe(self.on[DATABASE_RELATION].relation_broken, self._on_database_integration_broken)` in `__init__`
- [x] 6.7 Rename `_reconcile()` to `_holistic_handler()` and add NOOP_CONDITIONS guard at the top: `if not all(condition(self) for condition in NOOP_CONDITIONS): return`
- [x] 6.8 Replace `_on_event` delegation target: `_on_event` should call `self._on_holistic_handler(event)` (which wraps `_holistic_handler` with maintenance status, from the core-fixes pattern) or directly call `_holistic_handler()`
- [x] 6.9 Update `_holistic_handler()`: replace `self._db_integration` usage with `DatabaseConfig.load(self.database)`; remove the inline `can_connect` and `_ensure_database`/`_ensure_cluster` calls (now handled by NOOP_CONDITIONS and cluster check)
- [x] 6.10 Add `_on_pebble_ready(self, event: ops.PebbleReadyEvent)` method: calls `self._workload_service.open_port()`, then `self._on_holistic_handler(event)` (or `self._holistic_handler(event)` if no wrapper exists), then `self._workload_service.set_version()`
- [x] 6.11 Add `_on_pebble_check_failed(self, event: ops.PebbleCheckFailedEvent)` method: if `event.info.name == PEBBLE_READY_CHECK_NAME`, log a WARNING
- [x] 6.12 Add `_on_pebble_check_recovered(self, event: ops.PebbleCheckRecoveredEvent)` method: if `event.info.name == PEBBLE_READY_CHECK_NAME`, log an INFO
- [x] 6.13 Add `_on_database_integration_broken(self, event: ops.RelationBrokenEvent)` method: if `self._container.can_connect()`, call `self._container.stop(SERVICE_NAME)`
- [x] 6.14 Update `_on_collect_status` to use `container_connectivity(self)` instead of `self._container.can_connect()`; update database check to use `DatabaseConfig.load(self.database).is_ready()` or `database_resource_is_created(self)`; update cluster check to use `cluster_integration_exists(self)`; add service health checks after cluster checks:
  ```python
  can_connect = container_connectivity(self)
  if can_connect and self._workload_service.is_failing():
      event.add_status(ops.BlockedStatus("failed to start service, check container logs"))
  if can_connect and not self._workload_service.is_running():
      event.add_status(ops.WaitingStatus("waiting for service to start"))
  ```
- [x] 6.15 Remove the now-dead `_ensure_database()` and `_ensure_cluster()` helper methods from `src/charm.py`
