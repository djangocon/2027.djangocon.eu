<img src="djangocon/static/images/logo/logo_djceu27.png" height=100 />

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
section to that page. Add `published: false` to park a section without deleting
it — the homepage's speakers and news blocks are currently held that way.

Keep the metadata block unbroken: the parser stops at the first line that is not
`key: value`, so anything else (a stray heading, a blank line) turns the rest of
the block into body text.

**The homepage** is assembled the same way, from `content/home/*.md`. Each file
owns one band of the page and carries its copy, so the hero headline, the intro,
the ticket tiers and the important dates are all edited there rather than in a
template. `hero.md` also holds the date line and the CTA link in its metadata.

**Sponsors** live in `djangocon/content/sponsors.json`, grouped by tier. Copy an
existing entry to add one. Empty tiers are hidden automatically. `art` tells the
site how to keep a logo legible on both themes:

| `art`            | for artwork that is                        | what happens                     |
| ---------------- | ------------------------------------------ | -------------------------------- |
| `dark`           | dark or black line art                     | inverted to white on dark        |
| `light`          | white line art                             | darkened on light                |
| `colour`         | full colour, legible on either ground      | left alone                       |
| `colour-on-dark` | colour art with white lettering            | given a dark chip on light       |

**The menu** lives in `djangocon/content/navigation.json`. Submenu URLs must match
a folder under `content/` and end with a trailing slash. To hide an item without
deleting it, move it into the `_disabled` block.

## Design and theming

The site ships a light and a dark theme; visitors switch with the toggle in the
header, and the choice is remembered in `localStorage`. Without a stored choice
the site follows the operating system's preference.

All colours, type, spacing and motion are declared once in
`djangocon/static/sass/_variables.scss`. Brand values (the reds, black, white)
sit in `:root`; anything that differs between the themes is a *semantic* token —
`--bg`, `--surface`, `--fg`, `--fg-muted`, `--border` — redefined in the
`[data-theme='light']` block at the bottom of that file. Style new components
against the semantic tokens and they work in both themes with no extra rules.

Two details worth knowing before editing the theme:

- The initial theme is applied by an inline script in `base.html`, before the
  stylesheet paints. It has to stay inline and stay in `<head>`; moving it into
  `project.js` (which is deferred) reintroduces a flash of the wrong theme.
- The footer band is deliberately dark in *both* themes, matching the design, so
  it uses the fixed brand colours rather than the semantic ones.

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
