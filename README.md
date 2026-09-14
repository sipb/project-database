# project-database
Database for keeping track of project statuses.

## Development

First clone the repo.

Run dev server: `uv run project-database`

Reformat: `uv format`

Type checker: `uv check`

Linter: `ruff check`

Run tests (TODO figure out better command): `FLASK_DEBUG=0 PYTHONPATH=tests uv run python -m unittest test_authutils.Test_get_email -v`

## TODO

- Update docs
- Better CSS
- Run tests in CI
