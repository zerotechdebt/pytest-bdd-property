# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2026-11-09

### Changed

- CI now uses the locked tool versions (`uv.lock` is committed), fetches the shared specs, and runs the same checks as `just check-all`
- Releases are published to PyPI by GitHub Actions when a version tag is pushed (`just release`; see RELEASING.md)
- `__version__` is read from the installed package metadata, so the version only lives in `pyproject.toml`
- README shows CI, PyPI version and Python version badges

## [0.1.1] - 2026-11-08

### Changed

- Repository moved to zerotechdebt org (https://github.com/zerotechdebt/pytest-bdd-property); project URLs updated

## [0.1.0] - 2025-11-30

### Added

- Two-phase execution model: registration (Phase 1) then generation (Phase 2)
- 16 built-in strategies (text, integer, email, uuid, date, json, etc.)
- 18 built-in assumption patterns (equality, comparison, emptiness, length, containment, type checks)
- `property_when()` and `property_then()` step definition decorators
- `register_strategy()` and `register_assumption()` extension API
- Configuration tags: `@property-based`, `@num-runs:N`, `@seed:N`, `@verbose`
- pytest plugin entry point (`pytest11`)
- Conformance test suite against bdd-pbt-spec (40 RIDs)
- Local plugin specs (27 RIDs)
