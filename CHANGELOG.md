# Changelog

## [1.0.1](https://github.com/canonical/authentik-worker-operator/compare/v1.0.0...v1.0.1) (2026-07-24)


### Bug Fixes

* surface the worker version-gate status and cache the workload version ([baa390c](https://github.com/canonical/authentik-worker-operator/commit/baa390c8e6380ea395d3b73234e9a66d36b98bac))
* unblock worker startup, surface pebble failures, cache per event ([#36](https://github.com/canonical/authentik-worker-operator/issues/36)) ([f76e6ec](https://github.com/canonical/authentik-worker-operator/commit/f76e6ec8388c0bf64e17a23f95fbf94aff943ed5))

## 1.0.0 (2026-07-17)


### Features

* implement observability integrations and refactor charm architecture ([e26c398](https://github.com/canonical/authentik-worker-operator/commit/e26c398a46ee4652181248d5e1808c9916fb565e))
* implement pg connection pool and worker timeout configurations ([1defc9e](https://github.com/canonical/authentik-worker-operator/commit/1defc9e9aed1dcb2f9a3cd5aa9ca89f2a894aca3))
* implement pg connection pool and worker timeout configurations ([#33](https://github.com/canonical/authentik-worker-operator/issues/33)) ([14d139d](https://github.com/canonical/authentik-worker-operator/commit/14d139d35311020fb3852da732ed0ad42dd0c2db))


### Bug Fixes

* bump lib ([4e110af](https://github.com/canonical/authentik-worker-operator/commit/4e110af4977dda96394e5bfa486846f2df207750))
* **config:** prefix consumer_listen_timeout with seconds= ([c8dc36f](https://github.com/canonical/authentik-worker-operator/commit/c8dc36fbc69440be560481c85b47af8b669c3d97))
* **config:** prefix consumer_listen_timeout with seconds= ([#34](https://github.com/canonical/authentik-worker-operator/issues/34)) ([f68502d](https://github.com/canonical/authentik-worker-operator/commit/f68502d4b4ab1506e62a59da5e732be1f7dd0be4))
* define env vars ([f119c7e](https://github.com/canonical/authentik-worker-operator/commit/f119c7ece355be97ce61f76ca9e0da46060dab91))
* **deps:** update dependency cosl to ~=1.10.1 ([d0324b2](https://github.com/canonical/authentik-worker-operator/commit/d0324b22f42b3b4fe06331adfc5f7d0ec4e1d6b8))
* **deps:** update dependency cosl to ~=1.10.1 ([#27](https://github.com/canonical/authentik-worker-operator/issues/27)) ([fbb3d3e](https://github.com/canonical/authentik-worker-operator/commit/fbb3d3ec573116464ee5a35de1f42fb5c321ad3f))
* **deps:** update dependency cosl to ~=1.9.2 ([4a620f5](https://github.com/canonical/authentik-worker-operator/commit/4a620f5f6a570c296f1bc7f31faf99b565f0d76a))
* **deps:** update dependency cosl to ~=1.9.2 ([#14](https://github.com/canonical/authentik-worker-operator/issues/14)) ([4a2dd78](https://github.com/canonical/authentik-worker-operator/commit/4a2dd787abdb4129bc43f88b18886c2b060a332a))
* **deps:** update dependency lightkube to ~=0.22.0 ([24b195d](https://github.com/canonical/authentik-worker-operator/commit/24b195d4492952e455bdff809f18b2c3965afa43))
* **deps:** update dependency lightkube to ~=0.22.0 ([#23](https://github.com/canonical/authentik-worker-operator/issues/23)) ([a08d416](https://github.com/canonical/authentik-worker-operator/commit/a08d4160ed4222e2eb87e06820042ffa58878a49))
