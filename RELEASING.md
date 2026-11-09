# Releasing

Releases are published to PyPI by GitHub Actions when a version tag is pushed.
No PyPI token is needed: the [Release workflow](.github/workflows/release.yml)
uses PyPI trusted publishing.

## Steps

1. On `main`, bump `version = "X.Y.Z"` in `pyproject.toml`. That's the only
   place the version lives; `__version__` reads it from the installed package.
2. Add a `## [X.Y.Z] - YYYY-MM-DD` section to `CHANGELOG.md`.
3. Commit and push to `main`, and wait for CI to pass.
4. Run `just release`.

`just release` refuses to run unless you are on `main`, the tree is clean and
in sync with `origin/main`, the CHANGELOG has an entry for the version, and
the tag doesn't exist yet. It then runs `just ci`, creates the `vX.Y.Z` tag
and pushes it.

Pushing the tag starts the Release workflow, which:

1. runs the full CI checks,
2. fails if the tag doesn't match the `pyproject.toml` version,
3. builds the sdist and wheel,
4. publishes them to PyPI from the `pypi` environment.

Watch it with `gh run watch`, then check
https://pypi.org/project/pytest-bdd-property/.

## If the release workflow fails

- **Checks or build failed:** nothing was published. Fix it on `main`, delete
  the tag (`git push origin :refs/tags/vX.Y.Z && git tag -d vX.Y.Z`), and run
  `just release` again.
- **Publish step failed:** check the trusted publisher settings below. Then
  re-run the failed jobs from the Actions page. PyPI never accepts the same
  version twice, so if anything did upload, bump to the next patch version.

## One-time setup (both done as of 2026-11-09)

Only needed again if the repo or workflow file is renamed or moved.

- **PyPI trusted publisher.** On https://pypi.org/manage/project/pytest-bdd-property/settings/publishing/
  add a GitHub publisher with owner `zerotechdebt`, repository
  `pytest-bdd-property`, workflow `release.yml`, environment `pypi`.
- **GitHub environment.** The repo has an environment named `pypi`
  (Settings → Environments).

## Manual fallback

If GitHub Actions is unavailable, build and upload by hand with a
project-scoped API token from https://pypi.org/manage/account/token/:

```bash
rm -rf dist && uv build
uvx twine upload dist/*
```
