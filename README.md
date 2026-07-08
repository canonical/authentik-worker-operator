# Charmed Authentik Worker

[![CharmHub Badge][charmhub-badge]][charmhub]
[![Juju][juju-badge]][juju-link]
[![License][license-badge]][license-link]

[![Continuous Integration Status][ci-badge]][ci-link]
[![pre-commit][pre-commit-badge]][pre-commit-link]
[![Conventional Commits][cc-badge]][cc-link]

## Description

Charmed Authentik Worker is an operator that manages the Authentik Worker
application on Kubernetes using Juju. It handles background processes,
outposts, and other asynchronous tasks for the Authentik cluster (such as email
delivery, task synchronization, and background worker processes).

This operator ensures the worker is correctly configured and integrated within
the Authentik deployment, working in tandem with the core Authentik Server.

## Usage & Deployment

### Basic Deployment

The Authentik Worker is designed to run alongside the Authentik Server. It does
not integrate directly with the PostgreSQL database. Instead, the Authentik
Server integrates with PostgreSQL and shares the database credentials and the
encryption key with the Authentik Worker via the `authentik-cluster` relation.

To deploy a fully functioning Authentik instance with the worker:

```shell
# Deploy the PostgreSQL database operator
juju deploy postgresql-k8s --channel 14/stable --trust

# Deploy the Authentik Server operator
juju deploy authentik-server --trust

# Deploy the Authentik Worker operator (this charm)
juju deploy authentik-worker --channel latest/edge --trust

# Integrate Authentik Server with the PostgreSQL database
juju integrate postgresql-k8s authentik-server

# Integrate Authentik Server with the Authentik Worker
juju integrate \
  authentik-server:authentik-cluster \
  authentik-worker:authentik-cluster
```

You can track the deployment status using:
```shell
watch -c juju status --color
```

Once the charms settle into an `active` and `idle` status, the Authentik setup
is fully operational.

## Integrations

### Authentik Server (`authentik-cluster`)

An integration with [authentik-server-operator][server-operator] is
**required**. Through this relation, the worker receives the encryption key
(`AUTHENTIK_SECRET_KEY`) and the PostgreSQL database configuration/credentials
from the server. Without this, the worker cannot connect to the database or
decrypt cluster secrets.

### Observability

Charmed Authentik Worker offers integration with the Canonical Observability
Stack (COS) to forward logs, expose metrics, and export traces:

*   **Logging** (`logging`): Forward workload logs to Loki.
    ```shell
    juju integrate loki-k8s authentik-worker:logging
    ```
*   **Metrics** (`metrics-endpoint`): Expose Prometheus scrape endpoints.
    ```shell
    juju integrate prometheus-k8s authentik-worker:metrics-endpoint
    ```
*   **Tracing** (`tracing`): Send application trace data to Tempo.
    ```shell
    juju integrate tempo-k8s authentik-worker:tracing
    ```

## Scenarios

### Configuring Worker Performance

You can customize the worker's performance settings using Juju config options,
depending on your deployment load:

```shell
# Set the number of worker processes to start
# (maps to AUTHENTIK_WORKER__PROCESSES)
juju config authentik-worker worker_processes=2

# Set the number of Dramatiq threads per worker process
# (maps to AUTHENTIK_WORKER__THREADS)
juju config authentik-worker worker_threads=4
```

## Security

Please see [SECURITY.md](SECURITY.md) for guidelines on reporting security
issues.

## Contributing

Please see the [Juju SDK docs](https://juju.is/docs/sdk) for guidelines on
enhancements to this charm following best practice guidelines, and
[CONTRIBUTING.md](CONTRIBUTING.md) for developer guidance.

## License

The Charmed Authentik Worker is free software, distributed under the Apache
Software License, version 2.0. See [LICENSE](LICENSE) for more information.

[charmhub-badge]: https://charmhub.io/authentik-worker/badge.svg
[charmhub]: https://charmhub.io/authentik-worker
[juju-badge]: https://img.shields.io/badge/Juju%20-3.0+-%23E95420
[juju-link]: https://github.com/juju/juju
[license-badge]: https://img.shields.io/badge/License-Apache_2.0-blue.svg
[license-link]: LICENSE
[ci-badge]: https://github.com/canonical/authentik-worker-operator/actions/workflows/on_push.yaml/badge.svg?branch=main
[ci-link]: https://github.com/canonical/authentik-worker-operator/actions
[pre-commit-badge]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit
[pre-commit-link]: https://github.com/pre-commit/pre-commit
[cc-badge]: https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196.svg
[cc-link]: https://conventionalcommits.org
[server-operator]: https://github.com/canonical/authentik-server-operator
