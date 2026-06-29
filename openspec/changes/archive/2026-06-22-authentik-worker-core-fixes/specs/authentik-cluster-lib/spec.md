## ADDED Requirements

### Requirement: AuthentikClusterRequirerEvents exposes a ready event
`AuthentikClusterRequirerEvents` SHALL define a single `ready` event sourced from
`AuthentikClusterRequirerReadyEvent`. The obsolete `cluster_changed` and `cluster_removed`
events SHALL be removed.

#### Scenario: ready event is accessible
- **WHEN** `AuthentikClusterRequirer` is instantiated
- **THEN** `cluster.on.ready` is a valid event source
- **THEN** `cluster.on.cluster_changed` does not exist
- **THEN** `cluster.on.cluster_removed` does not exist

### Requirement: AuthentikClusterRequirer emits ready on relation_changed when data present
`AuthentikClusterRequirer` SHALL observe `relation_changed` and emit `on.ready` only when
`secret_key_secret_id` is present in the provider app databag.

#### Scenario: ready emitted when secret id arrives
- **WHEN** `relation_changed` fires and `secret_key_secret_id` is in the relation app databag
- **THEN** `on.ready` is emitted

#### Scenario: ready not emitted when secret id is absent
- **WHEN** `relation_changed` fires and `secret_key_secret_id` is not in the relation app databag
- **THEN** `on.ready` is NOT emitted

### Requirement: is_ready is a property
`AuthentikClusterRequirer.is_ready` SHALL be a Python property (not a method) that returns
`True` when `secret_key_secret_id` is present in the provider app databag.

#### Scenario: is_ready returns True when secret id present
- **WHEN** the relation app databag contains `secret_key_secret_id`
- **THEN** `cluster.is_ready` returns `True`

#### Scenario: is_ready returns False when no relation
- **WHEN** no `authentik-cluster` relation exists
- **THEN** `cluster.is_ready` returns `False`

#### Scenario: is_ready returns False when secret id absent
- **WHEN** the relation exists but `secret_key_secret_id` is not in the app databag
- **THEN** `cluster.is_ready` returns `False`

### Requirement: get_secret_key reads Juju secret by ID from databag
`AuthentikClusterRequirer.get_secret_key()` SHALL read `secret_key_secret_id` from the
provider app databag, retrieve the Juju secret by that ID, and return the `secret-key` value.
It SHALL return `None` if the relation is missing or the secret id is absent.

#### Scenario: Returns secret key when relation is ready
- **WHEN** the relation is ready and the Juju secret is accessible
- **THEN** `get_secret_key()` returns the string value of `secret-key`

#### Scenario: Returns None when relation is absent
- **WHEN** no `authentik-cluster` relation exists
- **THEN** `get_secret_key()` returns `None`

### Requirement: AuthentikClusterProvider fixes secret persistence
`AuthentikClusterProvider` SHALL look up the existing secret by label
`"authentik-secret-key"` on each call to `set_secret_key`, rather than relying on an
in-memory `_secret` field that is lost between Juju hook invocations.

#### Scenario: set_secret_key reuses existing secret across hooks
- **WHEN** `set_secret_key` is called and a secret labelled `"authentik-secret-key"` already exists
- **THEN** the existing secret content is updated rather than a new secret being created

#### Scenario: set_secret_key creates secret on first call
- **WHEN** `set_secret_key` is called and no secret labelled `"authentik-secret-key"` exists
- **THEN** a new Juju secret is created with label `"authentik-secret-key"`

### Requirement: charm.py observes cluster.on.ready
`charm.py` SHALL observe `cluster.on.ready` and route it to `_on_event`. Observation of
`cluster.on.cluster_changed` and `cluster.on.cluster_removed` SHALL be removed.

#### Scenario: ready event wired to reconcile
- **WHEN** `cluster.on.ready` fires
- **THEN** `_reconcile()` is called
