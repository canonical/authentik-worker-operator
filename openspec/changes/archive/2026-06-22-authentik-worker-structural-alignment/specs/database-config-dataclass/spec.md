## ADDED Requirements

### Requirement: DatabaseConfig is a frozen dataclass
`DatabaseConfig` in `src/integrations.py` SHALL be a `@dataclass(frozen=True, slots=True)` with fields: `host: str = ""`, `port: str = ""`, `user: str = ""`, `password: str = ""`, `name: str = ""`. The class replaces the former `DatabaseIntegration` class.

#### Scenario: Default construction
- **WHEN** `DatabaseConfig()` is constructed with no arguments
- **THEN** all fields are empty strings and the object is immutable (setting any field raises `FrozenInstanceError`)

#### Scenario: Construction with all fields
- **WHEN** `DatabaseConfig(host="db", port="5432", user="u", password="p", name="n")` is constructed
- **THEN** all fields hold the provided values

### Requirement: DatabaseConfig.to_env_vars returns PostgreSQL env vars
The `to_env_vars()` method SHALL return a dict with keys `AUTHENTIK_POSTGRESQL__HOST`, `AUTHENTIK_POSTGRESQL__PORT`, `AUTHENTIK_POSTGRESQL__USER`, `AUTHENTIK_POSTGRESQL__PASSWORD`, `AUTHENTIK_POSTGRESQL__NAME` populated from the dataclass fields. Fields may be empty strings.

#### Scenario: All fields populated
- **WHEN** `to_env_vars()` is called on a `DatabaseConfig` with all fields set
- **THEN** the returned dict contains all five `AUTHENTIK_POSTGRESQL__` keys with their values

#### Scenario: Default (empty) DatabaseConfig
- **WHEN** `to_env_vars()` is called on `DatabaseConfig()` (all defaults)
- **THEN** the returned dict contains all five keys with empty string values

### Requirement: DatabaseConfig.is_ready validates minimum required fields
The `is_ready() -> bool` method SHALL return `True` if and only if `host`, `port`, and `user` are all non-empty strings.

#### Scenario: All required fields present
- **WHEN** `DatabaseConfig` has non-empty `host`, `port`, and `user`
- **THEN** `is_ready()` returns `True`

#### Scenario: Host missing
- **WHEN** `DatabaseConfig` has empty `host`
- **THEN** `is_ready()` returns `False`

#### Scenario: Port missing
- **WHEN** `DatabaseConfig` has non-empty `host` but empty `port`
- **THEN** `is_ready()` returns `False`

### Requirement: DatabaseConfig.load classmethod parses relation data
The `load(cls, database: DatabaseRequires) -> "DatabaseConfig"` classmethod SHALL fetch relation data from `database.fetch_relation_data()` and construct a `DatabaseConfig`. If no relations exist or the data does not contain `"endpoints"`, it SHALL return `DatabaseConfig()`.

#### Scenario: Relation present with endpoint data
- **WHEN** `DatabaseRequires` has a relation with `endpoints`, `username`, `password`, and `database` fields
- **THEN** `DatabaseConfig.load(database)` returns a `DatabaseConfig` with `host`, `port`, `user`, `password`, `name` populated from that data

#### Scenario: No relation present
- **WHEN** `DatabaseRequires` has no relations
- **THEN** `DatabaseConfig.load(database)` returns `DatabaseConfig()` (all empty strings)

#### Scenario: Relation present but no endpoint data yet
- **WHEN** `DatabaseRequires` has a relation but `"endpoints"` is absent from relation data
- **THEN** `DatabaseConfig.load(database)` returns `DatabaseConfig()` (all empty strings)
