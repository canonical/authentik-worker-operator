## ADDED Requirements

### Requirement: CharmConfig exposes proxy environment variables
The `CharmConfig.to_env_vars()` method SHALL include `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY` in the returned env vars dict, sourced from charm config keys `http_proxy`, `https_proxy`, and `no_proxy` respectively. If a config key is absent or None, the corresponding env var SHALL be omitted (not set to an empty string).

#### Scenario: Proxy config set
- **WHEN** charm config has `http_proxy = "http://proxy:3128"`, `https_proxy = "http://proxy:3128"`, `no_proxy = "localhost"`
- **THEN** `to_env_vars()` includes `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY` with those values

#### Scenario: No proxy config set
- **WHEN** charm config has no `http_proxy`, `https_proxy`, or `no_proxy` keys (or they are None)
- **THEN** `to_env_vars()` does not include `HTTP_PROXY`, `HTTPS_PROXY`, or `NO_PROXY`

#### Scenario: Only http_proxy set
- **WHEN** charm config has `http_proxy = "http://proxy:3128"` but `https_proxy` and `no_proxy` are absent
- **THEN** `to_env_vars()` includes `HTTP_PROXY` but not `HTTPS_PROXY` or `NO_PROXY`
