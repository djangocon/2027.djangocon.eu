<img src="djangocon/static/images/logo/logo_djceu27.svg" height=100 />

🌍 [2027.djangocon.eu](https://2027.djangocon.eu/) \
📍 Innsbruck, Austria \
📅 Date TBD

[![built-with](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-blue.svg)](https://github.com/pydanny/cookiecutter-django/)
[![code-style](https://img.shields.io/badge/code%20style-ruff-261230.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)]()

## Local Development

### Using Docker

```bash
python setup_env.py
docker compose build
docker compose up
```

To access the running Django container, use `docker compose exec django /bin/bash`.

The site has no database and no models: every page is rendered from the Markdown
files in `djangocon/content/`. There is nothing to migrate.

### Using venv

! WARNING ! - Docker is recommended for local development, as the node container
compiles SCSS automatically (edits made directly to the CSS files WILL be
overwritten by the compiler). Using venv means installing node and npm yourself
and running `npm run dev` to watch and compile SCSS.

Requires Python 3.10 or newer (Django 5.2 LTS).

_optional_ - Create a virtual environment

```bash
python -m venv env
source env/bin/activate
```

install requirements:

```bash
pip install -r requirements/local.txt   # or production.txt
```



## Editing site content

No Python needed for any of this.

**Page text** lives in `djangocon/content/<section>/<page>/*.md`. Each file starts
with a small metadata block:

```
title: Grant Status
layout: simple
order: 2
```

`order` sets the position on the page, and `layout` picks a template from
`djangocon/templates/modules/`. A layout name that doesn't exist falls back to
`simple` rather than breaking the page. Adding a `.md` file to a folder adds a
section to that page.

**Sponsors** live in `djangocon/content/sponsors.json`, grouped by tier. Copy an
existing entry to add one. Empty tiers are hidden automatically. Set `filter` to
`true` when a dark logo needs inverting to white.

**The menu** lives in `djangocon/content/navigation.json`. Submenu URLs must match
a folder under `content/` and end with a trailing slash. To hide an item without
deleting it, move it into the `_disabled` block.

## Code of Conduct

As a contributor, you can help us keep the Django community open and inclusive.
Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

Get started contributing by reading our [Contributing](CONTRIBUTING.md) guidelines.

## How to Contribute to DjangoConEu website

To contribute to this project, please follow these steps:

1. Fork the Repo
2. Clone the Repo to your local machine
3. Follow "Local Development"
4. make changes and submit a PR( we will review)

## Built With

- [Python](https://docs.python.org/3/) - Programming language
- [Django](https://docs.djangoproject.com/) - Web framework

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
