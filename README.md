<picture>
  <source media="(prefers-color-scheme: light)" srcset="djangocon/static/images/logo/logo_djceu27_light.svg">
  <img src="djangocon/static/images/logo/logo_djceu27.svg" height="100" alt="DjangoCon Europe 2027 Innsbruck">
</picture>

🌍 [2027.djangocon.eu](https://2027.djangocon.eu/) \
📍 Innsbruck, Austria \
📅 17–21 February 2027

[![built-with](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-blue.svg)](https://github.com/pydanny/cookiecutter-django/)
[![code-style](https://img.shields.io/badge/code%20style-ruff-261230.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)]()

## Local development

Requirements: Docker and [just](https://just.systems) (`brew install just`).

```bash
just build   # creates .envs/.django if missing and builds the images
just up      # django on http://localhost:8000, browser-sync on http://localhost:3000
just logs    # follow the logs (or `just logs node`)
just down
```

`just` on its own lists every recipe. The node container watches `djangocon/static/sass`
and recompiles `project.css` on change — edit the SCSS, never the CSS. Other useful
recipes: `just manage <cmd>`, `just shell`, `just lint` (all pre-commit hooks),
`just pytest`, `just assets` (one-off SCSS/JS build), `just collectstatic`.

The site has no database and no models: every page is rendered from the files in
`djangocon/content/`. There is nothing to migrate.

### Without Docker

Python 3.13 and Node 22 are required (see `pyproject.toml` / `package.json`).

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements/local.txt
npm ci && npm run build          # or `npm run dev` to watch SCSS/JS
python manage.py runserver
```

### Code quality

Python is linted and formatted by [ruff](https://docs.astral.sh/ruff/), templates by
[djLint](https://djlint.com/), everything else by prettier — all wired through
pre-commit (`pre-commit install` once, or `just lint` to run everything).

## Deploying

Production settings live in `config/settings/production.py` and are driven by
environment variables: `DJANGO_SECRET_KEY` (required), `DJANGO_ALLOWED_HOSTS`
(default `2027.djangocon.eu`), `SENTRY_DSN` (optional), `DJANGO_SECURE_HSTS_SECONDS`
(default 60 — raise once HTTPS is proven). Static files are served by WhiteNoise
from `staticfiles/` after `manage.py collectstatic`; run the app with gunicorn
(`gunicorn config.wsgi`).

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
section to that page. Use `##`/`###` headings inside the body — the page title is
the only `<h1>`.

Some layouts carry their own copy in the template rather than in the `.md`
(`home_about`, `home_tickets`, `home_dates`, `past_edition`, `credits`); edit
those under `djangocon/templates/modules/`.

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
