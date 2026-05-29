# Havano branding assets (optional addon file copy)

Place files here to overwrite static assets inside other Odoo modules:

`havano_branding/<target_module>/<path/inside/module>/<file>`

Example:

- `havano_branding/web/static/img/favicon.ico`

## Built-in branding (recommended)

The module ships canonical files in:

`static/branding/`

- `company_logo.png` → all companies (`res.company.logo`, PDFs)
- `website_logo.png` → website logo + default social share image
- `favicon.ico` → website favicon
- `report_logo.png` → preferred logo for PDF/report headers

These are applied automatically on install and via **Settings → General Settings → Seed Havano Branding**.
