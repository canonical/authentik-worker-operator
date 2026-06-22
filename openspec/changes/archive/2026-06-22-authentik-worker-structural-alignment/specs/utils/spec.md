## ADDED Requirements

### Requirement: utils module provides NOOP_CONDITIONS tuple
The charm SHALL expose a `NOOP_CONDITIONS: tuple[Condition, ...]` in `src/utils.py` containing the ordered set of conditions that must all be true before a reconcile cycle can proceed. Each condition is a callable `(charm: AuthentikWorkerCharm) -> bool`.

#### Scenario: All conditions true
- **WHEN** the workload container is reachable, the database relation exists, and the database resource is created
- **THEN** `all(condition(charm) for condition in NOOP_CONDITIONS)` returns `True`

#### Scenario: Container not reachable
- **WHEN** `charm.unit.get_container(WORKLOAD_CONTAINER).can_connect()` returns `False`
- **THEN** `all(condition(charm) for condition in NOOP_CONDITIONS)` returns `False`

#### Scenario: Database relation absent
- **WHEN** `charm.model.relations[DATABASE_RELATION]` is empty
- **THEN** `all(condition(charm) for condition in NOOP_CONDITIONS)` returns `False`

#### Scenario: Database resource not yet created
- **WHEN** `charm.database.is_resource_created()` returns `False`
- **THEN** `all(condition(charm) for condition in NOOP_CONDITIONS)` returns `False`

### Requirement: container_connectivity condition
The `container_connectivity(charm)` function SHALL return `True` if and only if the workload container (identified by `WORKLOAD_CONTAINER`) can be connected to.

#### Scenario: Container reachable
- **WHEN** `charm.unit.get_container(WORKLOAD_CONTAINER).can_connect()` returns `True`
- **THEN** `container_connectivity(charm)` returns `True`

#### Scenario: Container not reachable
- **WHEN** `charm.unit.get_container(WORKLOAD_CONTAINER).can_connect()` returns `False`
- **THEN** `container_connectivity(charm)` returns `False`

### Requirement: database_integration_exists condition
The `database_integration_exists(charm)` function SHALL return `True` if and only if at least one relation on the `DATABASE_RELATION` endpoint exists.

#### Scenario: Relation present
- **WHEN** `charm.model.relations[DATABASE_RELATION]` contains at least one relation
- **THEN** `database_integration_exists(charm)` returns `True`

#### Scenario: Relation absent
- **WHEN** `charm.model.relations[DATABASE_RELATION]` is empty
- **THEN** `database_integration_exists(charm)` returns `False`

### Requirement: database_resource_is_created condition
The `database_resource_is_created(charm)` function SHALL return `True` if and only if `charm.database.is_resource_created()` returns `True`.

#### Scenario: Resource created
- **WHEN** `charm.database.is_resource_created()` returns `True`
- **THEN** `database_resource_is_created(charm)` returns `True`

#### Scenario: Resource not yet created
- **WHEN** `charm.database.is_resource_created()` returns `False`
- **THEN** `database_resource_is_created(charm)` returns `False`

### Requirement: cluster_integration_exists condition
The `cluster_integration_exists(charm)` function SHALL return `True` if and only if `charm.model.get_relation(CLUSTER_RELATION)` returns a non-None relation.

#### Scenario: Relation present
- **WHEN** the `authentik-cluster` relation exists in the model
- **THEN** `cluster_integration_exists(charm)` returns `True`

#### Scenario: Relation absent
- **WHEN** no `authentik-cluster` relation exists
- **THEN** `cluster_integration_exists(charm)` returns `False`
