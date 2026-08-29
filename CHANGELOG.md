# Changelog

## [1.1.1](https://github.com/canonical/authentik-worker-operator/compare/v1.1.0...v1.1.1) (2026-08-29)


### Bug Fixes

* **authentik_cluster:** stop re-issuing the secret-backend token every hook ([ce6e9b5](https://github.com/canonical/authentik-worker-operator/commit/ce6e9b5be23d5790a64a7aaae57d75b1f7706886))
* **deps:** update dependency lightkube-models to ~=1.37.0.8 ([6650416](https://github.com/canonical/authentik-worker-operator/commit/665041621e5748a303c50083b037298f092e3302))
* **deps:** update dependency lightkube-models to ~=1.37.0.8 ([#63](https://github.com/canonical/authentik-worker-operator/issues/63)) ([91cc129](https://github.com/canonical/authentik-worker-operator/commit/91cc129dc27775057c67d9954a7be79c0e846d41))
* **terraform:** declare a minimum Juju provider version ([#54](https://github.com/canonical/authentik-worker-operator/issues/54)) ([a0e6019](https://github.com/canonical/authentik-worker-operator/commit/a0e6019c44c67052e682d7214d91f228fd487705))
* **terraform:** declare a minimum Juju provider version, not a pessimistic one ([bfca331](https://github.com/canonical/authentik-worker-operator/commit/bfca331e849c30d1561cbf29b6bfd37c236daa19))

## [1.1.0](https://github.com/canonical/authentik-worker-operator/compare/v1.0.1...v1.1.0) (2026-08-19)


### Features

* add working COS metrics, alert rules and dashboard ([21cc013](https://github.com/canonical/authentik-worker-operator/commit/21cc013032a42fffb091f05a50edd3f069ee9a68))
* add working COS metrics, alert rules and dashboard ([#48](https://github.com/canonical/authentik-worker-operator/issues/48)) ([499f971](https://github.com/canonical/authentik-worker-operator/commit/499f9710844409794e00b24737bbd484234d65ad))


### Bug Fixes

* consume PostgreSQL read replicas and PgBouncer flag from the server ([246de2f](https://github.com/canonical/authentik-worker-operator/commit/246de2fcd6c826f51d585578b04bd496d4a25e59))
* **deps:** update dependency lightkube to v1 ([3e9cfcf](https://github.com/canonical/authentik-worker-operator/commit/3e9cfcf702b57950921d5bfb014571391bb97122))
* **deps:** update dependency lightkube to v1 ([#47](https://github.com/canonical/authentik-worker-operator/issues/47)) ([bf23f1f](https://github.com/canonical/authentik-worker-operator/commit/bf23f1f01bd6f67122d300b0293073312f3d7024))
* **deps:** update dependency lightkube-models to ~=1.36.3.8 ([e2c2348](https://github.com/canonical/authentik-worker-operator/commit/e2c234880b687115921750ab1e292c916ba28817))
* **deps:** update dependency lightkube-models to ~=1.36.3.8 ([#42](https://github.com/canonical/authentik-worker-operator/issues/42)) ([9560f30](https://github.com/canonical/authentik-worker-operator/commit/9560f301b3c824e8d73088bef772ce411f242985))
* emit worker status promptly and stop on version mismatch ([c664a8a](https://github.com/canonical/authentik-worker-operator/commit/c664a8ae403408845609b927da3639643c3d1fa9))
* emit worker status promptly and stop on version mismatch ([#40](https://github.com/canonical/authentik-worker-operator/issues/40)) ([5f3060c](https://github.com/canonical/authentik-worker-operator/commit/5f3060cc844df69840e982a048aeb94e012fc126))
* **terraform:** align juju provider constraint with sibling modules ([e19d996](https://github.com/canonical/authentik-worker-operator/commit/e19d9962f55c086de58bc1ee1b4c6c3bde29b8aa))

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
