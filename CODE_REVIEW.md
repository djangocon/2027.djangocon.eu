# 2027.djangocon.eu — code & content review

Reviewed on 2026-09-05 against `main` (ae127b4). Everything under `config/`, `djangocon/`, the build/compose files and all 80 Markdown content files were read. The Figma (`djangoconeu_27`, Desktop‑8 light / Desktop‑9 dark) was used as the design reference; per David, the **dark frame is the accurate one** — the light frame only shows the colour mapping. The site itself follows the OS theme preference by default.

## Changes already made in this pass

1. **Hero parallax** (`_homepage.scss`, `project.js`). The sticky/50vh‑runway construction is replaced by a two‑layer parallax: the headline is the far layer (moves at ~0.35× page speed and fades out over the first 70vh), the mountain is the near layer (stays in flow, swells 8% from its base) so it slides up over the copy with no gap before "Run by the community". The silhouette also slides in from below on first paint. CSS scroll‑driven animations (`animation-timeline: scroll(root)`) do the work; `project.js` feeds the same curve through `--hero-p` for browsers without them (Firefox); `prefers-reduced-motion` gets the static layout. Note `overflow: clip` on `.hero-section` — `hidden` would have made the section itself the scroll container that `scroll()` binds to (this was the first thing that bit me).
2. **Theme bootstrap** (`base.html`). Still follows the OS preference (toggle choice remembered); the `localStorage` read is now wrapped in try/catch and a `<meta name="color-scheme">` was added.
3. **Logo naming** (`header.html`, `README.md`). `logo_djceu27.svg` is now the base (light‑on‑dark) logo used by the dark theme; the black‑text variant is `logo_djceu27_light.svg`. The README uses a `<picture>` so GitHub shows the right one in either scheme.
4. `project.css`, `project.min.css`, `project.min.js` rebuilt (dart‑sass 1.93.1 + autoprefixer + cssnano, terser). The Bootstrap portion of the diff is colour‑notation noise from the newer sass; the Docker node container will regenerate it anyway.

---

## Status after the code pass (2026-09-05, second commit)

Every item under **Code** below has been addressed except where noted; the **Content** section is untouched and still needs the organising team.

Done: hero parallax; logo naming; theme bootstrap hardening; mountain images unchanged (needs a designer export — see below); Swiper/home*speakers, home_news, about.html, `djangocon/wsgi.py`, `utils/storages.py`, popup JS and `_carousel.scss` removed; Alpine, `sharp`, `svgo`, `node-sass-tilde-importer` and the no-op `imgCompression` dropped from the build (vendors.js is now just Bootstrap's bundle); ~36 MB of Porto/Vigo/Dublin assets and the unlicensed fonts deleted; Anymail/Mailgun, `EMAIL*\*`, `ADMINS`, `django.forms`, `contenttypes`, `LocaleMiddleware`/i18n removed and Sentry made optional; `CONTENT_DIR`is a setting and the loaders live in`site/utils/content.py`; `default_view`split into`home`/`sponsors`/`page`with explicit URLs and a 301 from`/home/`; one `<h1>`per page (section titles are`<h2>`, ids/classes are slugified, footer heading is a `<p>`); `404.html`uses`{% static %}`; grant checker rebuilt without `innerHTML`/`alert()`and reads its endpoint from`status_url:`in the`.md`; manifest/favicon links fixed; Open Graph/Twitter/canonical tags added; Google Fonts import trimmed to the five families in use; mobile sub-menus use Bootstrap collapse (accordion) instead of the inline script; `justfile`, cookiecutter-style `pyproject.toml`(ruff rule set, djLint, pytest), pre-commit with djLint + pyproject-fmt, README rewritten.`ruff`, `ruff format`, `djlint --lint/--check`, `prettier --check`, `pyproject-fmt --check`, `django-upgrade`and the pre-commit-hooks checks all pass;`manage.py check --deploy` is clean.

Still open (needs a decision or a designer, not code): the two mountain PNGs (dark is the reference; the light one should be re-exported at the same frame/size), self-hosting the Google Fonts, raising `DJANGO_SECURE_HSTS_SECONDS` in the deployment env, adding the three smoke tests / CI / a production Dockerfile (declined for now), the `.devcontainer` `~/.ssh` mount, and the hardcoded 2025 roster in `credits.html`.

---

## Code

### Bugs / things that will actually bite

- **Mountain images have different aspect ratios.** `mountain_innsbruck_light.png` is 3406×595 with transparency; `mountain_innsbruck_dark.png` is 3408×841 and fully opaque (its own black background). Toggling the theme changes the hero height by ~40% and shifts everything below. Export both from the same frame, same size, transparent background. Since the dark Figma frame is the reference, the dark PNG is the one to match.
- **`home_speakers.html` uses `Swiper`, which is not bundled** (`vendors.js` = Bootstrap + Alpine). Including it would throw at `DOMContentLoaded`. It is currently not included from `home.html`, so it is dead code — delete or bundle Swiper before re‑enabling.
- **`site.webmanifest`** has empty `name`/`short_name` and icon `src` paths at the web root (`/android-chrome-192x192.png`) that do not exist — they live under `/static/images/favicons/`. Also `base.html` points every `<link rel=icon>` at `favicon.png` although 16/32/180 variants exist.
- **`404.html`** hardcodes `/static/images/other/404.gif` (bypasses `{% static %}` → no cache‑busting under `CompressedManifestStaticFilesStorage`) and has no `alt`.
- **`grant_status.html`**: ships a `<body>` tag inside a module, uses `alert()`, and injects `data.fullName/remarks/vouchers` via `innerHTML` (XSS if the Apps Script ever returns attacker‑controlled text — use `textContent`). The Apps Script URL is the 2025 deployment.
- **Multiple `<h1>` per page.** `base.html` emits a hidden `<h1>` and `simple.html`/`composed.html` render each section title as `<h1>` → 5–10 h1s per page. Use `<h2>` for sections. Related: `<a id="{{ title }}">` produces ids with spaces (`your_rights.md` links to `#your%20rights`) and class names like `Let's Go Have some fun-row` — slugify the title once in the view and expose it in the context.
- **`<a><button>` nesting** in Markdown content (`t-shirts`, `visibility_options`) is invalid HTML. Use `<a class="hero-btn">` only.
- **`/` and `/home/` are two URLs for the same page** (`navigation.json` `"home": "/home/"`). Either redirect `/home/` or link the logo to `/`; add `<link rel="canonical">`.

### Dead / unnecessary code

- `djangocon/wsgi.py` (second WSGI module, points at _local_ settings), `djangocon/utils/storages.py` (empty), `djangocon/templates/pages/about.html` (only `{% extends %}`), `home_news.html` + `latest_news.md` and `speakers.md` (never included), `credits.md` body (template hardcodes names), `openPopup/closePopup` in `project.js` (no `#popup` in any template).
- **Alpine.js** is bundled (~45 KB min) but no template uses `x-data`. Drop it from `vendorsJs`.
- `LocaleMiddleware` + `USE_I18N` with no translations; `django.forms` + `FORM_RENDERER` with no forms; `django.contrib.contenttypes` with no models. Harmless, but the settings read as if this were an app with a database.
- **Anymail/Mailgun** in production settings is _required_ (`env("MAILGUN_API_KEY")` raises if unset) but the site sends no email. Either drop `django-anymail`, `EMAIL_*`, `ADMINS`, or make them optional. Same for `SENTRY_DSN` (fine to require, but document it).
- `gulpfile.mjs` `imgCompression` re‑encodes only the top level of `static/images` (all images live in subfolders), with `sharp(input).toBuffer()` and no options — it is a no‑op that rewrites files on every `gulp build`. Remove or make it recursive with actual compression settings.
- `static/fonts/` contains Product Sans (Google's proprietary UI font — not licensed for redistribution) and Florent, neither referenced by any `@font-face`, plus three stray images (`photo.jpg`, `google-product-sans.jpg`, `opengraph_color_1200dp.png`). Delete the fonts; move the OG image to `images/`.
- ~60 MB of legacy static assets from Porto/Vigo/Dublin: `images/hotels/*` (Porto hotels), `images/past/vigo_venue.png`, `arena.png`, `super_bock_arena_logo.png`, `docs/porto-card.pdf`, `docs/tap.pdf`, `home_carousel/*` (12 MB, unused), `speakers/current/*`, `venue/` (4.8 MB). Whitenoise gzips/brotlis all of it at `collectstatic`.

### Structure & style

- `views.py`, `content.py` and `context_processors.py` import `APPS_DIR` from `config.settings.base` instead of `django.conf.settings`. Works, but bypasses the settings override chain and couples the app to the settings module path. Expose `CONTENT_DIR = APPS_DIR / "content"` as a setting and read `settings.CONTENT_DIR`.
- `default_view` mixes routing and rendering decisions (`if menu == "home" … elif menu == "sponsors" and submenu == "sponsors"`). Two small views (`home`, `page`) plus an explicit `path("sponsors/sponsors/", …)` would be clearer than special‑casing inside one view. The `ctx["files"]["home"] = SPONSORS_PAGE` line is unused by `home.html`.
- `render_markdown_file` is in `templatetags/markdown_extras.py` but is imported by the view — it belongs in `site/utils/content.py` next to the JSON loaders.
- Home modules (`home_about.html`, `home_tickets.html`, `home_dates.html`, `past_edition.html`, `credits.html`) **hardcode their copy**; the README promises "every page is rendered from the Markdown files". Content editors editing `about.md` will see nothing change. Either move the text into the `.md` (and read `content.html`) or document which pages are template‑only.
- `README` says Python 3.10+, `pyproject` targets py313 and the Dockerfile uses 3.13. Pick one (3.12+ is fine with Django 5.2).
- `SECURE_HSTS_SECONDS = 60` still carries the cookiecutter TODO — raise to 31536000 once the domain is stable.
- `.pre-commit-config.yaml` installs `djlint` via requirements but never runs it; prettier excludes templates. Add the `djlint` hook (`--reformat` + `--lint`) so the templates get the same treatment as the Python.
- No tests at all (`pytest`/`pytest-django` are in `local.txt`). Three cheap ones would catch most regressions: every folder under `content/` renders 200; every `navigation.json` URL resolves; every `.md` `layout:` maps to an existing template.
- No production compose / Dockerfile target (the `BUILD_ENVIRONMENT` arg is there, nothing uses it), no CI. The `.devcontainer` binds `~/.ssh` and `/tmp` into the container — unusual for a static site; consider dropping.
- `base.html`: no Open Graph / Twitter card tags (there is an OG image in `static/fonts`), obsolete `x-ua-compatible` meta, fonts still fetched from Google Fonts (`@import` in `_base.scss`) — the only third‑party request left, and it contradicts both the "no CDN" comment and the privacy guide. Self‑host Anton/Anton SC/Lato (the only families actually used — Lexend Deca, Manrope, Modak appear only in the `@import`).
- `header.html` has an inline script for the mobile sub‑menus that duplicates what Bootstrap collapse already does with `data-bs-toggle`; it also toggles the `.collapse` class by hand, fighting Bootstrap's own state.
- Two Slack invite links in use (`zt-340erqj3r…` everywhere, `zt-1gjg5lqkz…` in `cfp/0_cfp.md`). Keep one, ideally as a value in `navigation.json` and referenced from content.

---

## Content

### Stale 2024/2025 material that is live right now

| Page                                                | Problem                                                                                                                                                                                                                                                   |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `information/tshirts`                               | Links to pretix **`djceu2025`**, shows the 2025 shirt, and announces a shirt that doesn't exist yet ("has arrived").                                                                                                                                      |
| `about/contact/2_faqs.md`                           | Two ticket links to **`djceu2025`**; a commented FAQ still describes Vigo train stations. "Invitation letters: coming soon" contradicts the visa guide, which offers them via `diversity@djangocon.eu`.                                                   |
| `information/announcements/1_transparencyreport.md` | This is the **2025 Dublin CoC transparency report** relabelled "2027" — "this year's conference", Irish privacy law, 35 talks, named team. Publishing it as 2027 is misleading. Re‑title it "2025 transparency report" (or remove until after the event). |
| `information/social_events/0_soon.md`               | "Mar de Vigo Auditorium Rooftop, June 7" (2024), DALL‑E image. The `socialevent_page` template ignores the `.md` body anyway and prints its own TBA text — so the file is both stale and unused.                                                          |
| `information/django_girls/*`                        | Title "Django Girls **Vigo**". Hidden from nav but reachable at `/information/django_girls/`.                                                                                                                                                             |
| `information/grants/*`                              | "Opportunity grants applications are **now closed**" — for 2027 they haven't opened (home says they open 30 Nov). The status checker calls the 2025 Apps Script.                                                                                          |
| `information/hospitality/1_childcare.md`            | "Applications open March 1, close March 31" — that is _after_ a February conference; home says childcare opens 7 Jan. Form link is 2025's.                                                                                                                |
| `about/credits`                                     | Hardcoded 2025 Dublin team.                                                                                                                                                                                                                               |
| `sponsors/sponsorship/1_visibility_options.md`      | `djc-sponsorship-brochure.pdf` is the previous edition's brochure (check prices/venue inside).                                                                                                                                                            |
| `talks/cfp/0_cfp.md`                                | "It's a new year…" framing; `1_schedule.md` links to a schedule page that says "Coming soon".                                                                                                                                                             |

### Internal contradictions

- **Venue**: `venue/0_venue.md` and the FAQ say "to be announced", while `code_of_conduct.md`, `response_guide/1_venue_and_local_context.md` (with street address) and `privacy_guide/who_we_are.md` name **Congress Innsbruck + Universität Innsbruck**. Decide whether it is public.
- **Edition number**: `home/about.md` says 17th, `sponsorship/0_sponsorships.md` says 18th.
- **Ticket prices**: templates show 59 / 99 / 299 / 399 €; the Figma shows 55 / 150 / 285 / 385 €. Confirm with the designer which is real (Figma values look like placeholders, but the tiers should match pretix).
- **Dates**: `home_dates.html` months have no year and the `dates.md` file is empty — the dates are hardcoded in the template. Announcements page says "Published: TBA".
- **Privacy guide**: `cookies.md` describes Google Analytics and a cookie banner; the site has neither (only a `localStorage` theme key — no banner needed, say so). `retention.md` still contains the placeholder `[X months/years — …]`. `0_privacy_guide.md` opens with "**Ad** Evolutio" (typo for "At"/"Evolutio"?). `legal_basis.md` refers to "what's described below" but nothing follows in that section.
- `talks/cfp/5_selection_process.md` duplicates `talks/selection_process/2_selection_process.md` word for word.
- `sponsors/jobs/jobs.md`: `order: 0` sits inside the HTML comment, so the meta block is malformed (harmless today, single file).
- README says "📅 Date TBD"; the site says 17–21 February 2027. README also references `djangocon/static/images/logo/logo_djceu27.svg` correctly but claims content is 100% Markdown (see above).
- Footer social list has no Mastodon although `external_logo/logo_fosstodon.svg` is shipped; X is still labelled "Twitter" in `navigation.json` keys (drives the icon filename, fine) — but the copy alternates between "X (formerly Twitter)" and "X".

### Copy nits

- `mentorship/0_info.md` mentions "Talk, Charla, Tutorial, or Poster" — "Charla" is a PyCon ES format, not DjangoCon Europe's.
- `sprints/0_sprints.md`: "there will a pool" → "there will be a pool"; "feel motivated do something" → "to do something".
- `faqs`: "get back you" → "get back to you"; "ticket kindly check it here" → "For everything concerning tickets, see …".
- `hospitality/1_childcare.md`: "March 31th".
- `visa_guide`: fee "currently €90" — fine, but add "as of 2026" or link only.

---

## Suggested order of work

1. Purge/relabel the 2024‑2025 leftovers (table above) — these are user‑visible today.
2. Resolve venue/edition/price contradictions with the organising team.
3. Fix the mountain image pair (same frame, same size) so theme toggling doesn't reflow the hero.
4. Trim dependencies (Alpine, Anymail, fonts, legacy assets), add the three smoke tests and djlint to pre‑commit.
5. Move hardcoded home copy into the Markdown files, or amend the README.
