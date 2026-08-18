# Observability Stack

## Purpose

Defines the Authentik Worker charm's observability integrations — Loki log
forwarding, Prometheus metrics scraping, Grafana dashboards, and tracing — so
operators receive logs, metrics, dashboards, and traces for the background task
workload out of the box.

The worker's surface mirrors the server's, with two deliberate differences: the
relation-name constants are spelled differently in `src/constants.py`, and the
worker's alert rules and dashboard describe background task health rather than
HTTP traffic.

## Requirements

### Requirement: Charm must integrate with Loki via LogForwarder

`charm.py` MUST instantiate `LogForwarder` from `charms.loki_k8s.v1.loki_push_api`
and bind it to the `logging` relation (`LOGGING_RELATION = "logging"`).
No explicit event wiring is required — `LogForwarder` handles forwarding passively.

#### Scenario: Log forwarding integration completes without error

Given the charm is deployed, when
`juju integrate authentik-worker:logging loki-k8s:logging` is run, then the
integration completes without errors and worker logs are forwarded to Loki.

### Requirement: Charm must expose Prometheus metrics via MetricsEndpointProvider

`charm.py` MUST instantiate `MetricsEndpointProvider` from
`charms.prometheus_k8s.v0.prometheus_scrape` with job name
`authentik_worker_metrics`, targeting port `METRICS_PORT` (9300) on all units
(`*:{METRICS_PORT}`) with the default `/metrics` path. The relation name is
`METRICS_RELATION = "metrics-endpoint"`.

Authentik serves its Prometheus registry on a dedicated metrics listener on
9300, not on the main HTTP port. `METRICS_PORT` MUST NOT be passed to
`unit.open_port()`: `prometheus_scrape` publishes the pod IP, so Prometheus
reaches it pod-to-pod, and opening it would expose unauthenticated metrics
through the Kubernetes Service. The charm's only `open_port()` call is
`WorkloadService.open_port()` in `src/services.py`, which opens `HTTP_PORT`
(9000) for the health endpoints and nothing else.

#### Scenario: Prometheus metrics integration completes without error

Given the charm is deployed, when
`juju integrate authentik-worker:metrics-endpoint prometheus-k8s:metrics-endpoint`
is run, then Prometheus can scrape metrics from `/metrics` on port 9300.

#### Scenario: Metrics port is not published on the Kubernetes Service

Given the charm is deployed, when the application's Kubernetes Service is
inspected, then port 9300 is absent from it.

### Requirement: Charm must provide Grafana dashboard via GrafanaDashboardProvider

`charm.py` MUST instantiate `GrafanaDashboardProvider` from
`charms.grafana_k8s.v0.grafana_dashboard` bound to
`GRAFANA_RELATION = "grafana-dashboard"`.
A dashboard template MUST exist at
`src/grafana_dashboards/authentik-worker.json.tmpl`.

#### Scenario: Grafana dashboard integration completes without error

Given `src/grafana_dashboards/authentik-worker.json.tmpl` exists and the charm is
deployed, when
`juju integrate authentik-worker:grafana-dashboard grafana-k8s:grafana-dashboard`
is run, then the dashboard template is sent to Grafana without errors.

### Requirement: Charm must send traces to Tempo via TracingEndpointRequirer

`charm.py` MUST instantiate `TracingEndpointRequirer` from
`charms.tempo_coordinator_k8s.v0.tracing` with `protocols=["otlp_http"]` and
`TRACING_RELATION = "tracing"`.

`integrations.py` MUST implement `TracingData` implementing `EnvVarConvertible`,
constructed via the `TracingData.load(requirer)` classmethod:

- `to_env_vars()` MUST return `{}` when the tracing endpoint is not ready.
- `to_env_vars()` MUST return `{"OTEL_EXPORTER_OTLP_ENDPOINT": <endpoint>}` when ready.

`TracingData` MUST be merged into the env var dict during reconciliation.

#### Scenario: Tracing env vars are absent when not integrated

Given no `tracing` relation exists, when `TracingData.to_env_vars()` is
called, then an empty dict `{}` is returned.

#### Scenario: Tracing env vars are set when endpoint is ready

Given a `tracing` relation is established and the endpoint is available, when
`TracingData.to_env_vars()` is called, then
`{"OTEL_EXPORTER_OTLP_ENDPOINT": "<endpoint-url>"}` is returned.

#### Scenario: Tracing integration connects without error

Given the charm is deployed, when
`juju integrate authentik-worker:tracing tempo-coordinator-k8s:tracing` is run,
then the integration completes and the OTLP endpoint env var is passed to the
workload.

### Requirement: Prometheus and Loki alert rule files must exist

The following alert rule files MUST exist in the charm source:

- `src/prometheus_alert_rules/authentik_worker_unavailable.rule` — fires
  `AuthentikWorkerUnavailable-multiple` when fewer than 70% of units are up for
  5 minutes, and `AuthentikWorkerUnavailable-all` when every unit is down for
  5 minutes.
- `src/prometheus_alert_rules/authentik_worker_task_backlog.rule` — fires
  `AuthentikWorkerTaskBacklog` when more than 100 background tasks remain queued
  for 15 minutes, indicating the worker is not draining its queue.
- `src/loki_alert_rules/authentik_worker_high_severity_log.rule` — fires
  `HighFrequencyHighSeverityLog` when error-or-above log entries exceed 100 in
  5 minutes.

`authentik_tasks_queued` is reported by both the server and the worker, so the
backlog expression MUST de-duplicate with
`max by (juju_model, juju_application, queue_name, actor_name)` before summing.
The Juju topology labels are load-bearing: dropping them collapses the maximum
across models and applications, and a naive `sum()` double-counts across
processes and units.

#### Scenario: Alert rule files are present in the charm

Given the charm is packed with `charmcraft pack`, when the resulting archive is
inspected, then all alert rule files are present at their expected paths.

### Requirement: Observability relation name constants must be defined in src/constants.py

`src/constants.py` MUST export the following constants so that `charm.py` can
reference relation names without string literals:

```python
LOGGING_RELATION = "logging"
TRACING_RELATION = "tracing"
METRICS_RELATION = "metrics-endpoint"
GRAFANA_RELATION = "grafana-dashboard"
```

#### Scenario: Constants are importable and match charmcraft.yaml relation names

Given the constants are defined in `src/constants.py`, when each constant is
compared against the corresponding relation name in `charmcraft.yaml`, then all
values match.

### Requirement: Terraform module must expose observability endpoints

`terraform/outputs.tf` MUST list every observability endpoint the charm declares,
so that consuming modules have a single authoritative source for the endpoint
names. The `provides` map MUST include both `metrics-endpoint` and
`grafana-dashboard`, and the `requires` map MUST include both `logging` and
`tracing`.

#### Scenario: Terraform outputs match charmcraft.yaml

Given `terraform/outputs.tf` and `charmcraft.yaml` are both parsed, when the
endpoint names in the `provides` and `requires` output maps are compared against
the endpoints declared in `charmcraft.yaml`, then every declared observability
endpoint appears in the corresponding output map.
