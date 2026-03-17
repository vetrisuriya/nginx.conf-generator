# Nginx Configuration Generator

This project now includes a **visual web application** for dynamically creating `nginx.conf` with a live preview.

## What you can generate

- MIME type include + `default_type`
- Standard directives and list-style directives
- `http`, `server`, `location`, and `upstream` blocks
- Variables in directives (for example `$host`, `$request_uri`)
- Location matching preferences:
  - exact `=`
  - preferential prefix `^~`
  - regex `~` / `~*`
  - normal prefix
- Redirects and rewrites
- `try_files` and named locations
- Load balancing (`upstream`)
- Logging (`error_log`, `access_log`)

## Web App (recommended)

Run a local static server from the repo root:

```bash
python3 -m http.server 4173
```

Then open:

- `http://localhost:4173/webapp/`

### Features

- Live `nginx.conf` preview while typing
- Add/remove location blocks dynamically
- Automatic location ordering by nginx precedence
- One-click **Download nginx.conf**
- Reset to working defaults

## CLI Generator (also available)

A Python JSON-based generator is included as `nginx_conf_generator.py`.

```bash
python3 nginx_conf_generator.py --input examples/site_spec.json --output nginx.conf
```

## Tests

```bash
python3 -m pytest -q
```
