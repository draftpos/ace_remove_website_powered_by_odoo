# -*- coding: utf-8 -*-

import base64
import logging
import shutil
from pathlib import Path

from odoo import _, api, models
from odoo.modules.module import get_module_path
from odoo.tools import config

_logger = logging.getLogger(__name__)

HAVANO_COPYRIGHT = 'Copyright © Havano'


class HavanoRebranding(models.TransientModel):
    """Automatic rebranding and branding asset seeding for Havano."""

    _name = 'havano.rebranding'
    _description = 'Havano Auto Rebranding'

    IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.svg', '.gif', '.webp', '.ico'}

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    @api.model
    def run_full_seed(self):
        """Apply full Havano branding (install hook + manual seed button)."""
        _logger.info('=' * 60)
        _logger.info('HAVANO FULL BRANDING SEED START')
        _logger.info('=' * 60)

        self.seed_branding_images()
        self._apply_branding_assets()
        self.auto_rebrand()
        self._patch_footer_copyright_view()

        _logger.info('=' * 60)
        _logger.info('HAVANO FULL BRANDING SEED COMPLETE')
        _logger.info('=' * 60)
        return True

    @api.model
    def auto_rebrand(self):
        """Text/parameters rebranding (company metadata, emails, portal)."""
        self._rebrand_company_metadata()
        self._rebrand_email_templates()
        self._rebrand_system_parameters()
        self._rebrand_portal()
        return True

    def action_seed_branding_images(self):
        self.ensure_one()
        self.run_full_seed()
        return self._notification(_('Branding Seeder'), _('Havano branding seeding completed.'))

    def action_auto_rebrand(self):
        self.ensure_one()
        self.run_full_seed()
        return self._notification(
            _('Havano Rebranding'),
            _('Auto rebrand and branding seeding completed.'),
        )

    # -------------------------------------------------------------------------
    # Branding assets (logos, favicon, website, company, PDFs)
    # -------------------------------------------------------------------------

    @api.model
    def _apply_branding_assets(self):
        """Push bundled images into company, website logo, favicon, and social image."""
        assets = self._load_branding_assets()
        if not assets:
            _logger.warning('No Havano branding image files found; skipping asset apply.')
            return False

        company_logo = assets.get('company_logo')
        website_logo = assets.get('website_logo') or company_logo
        favicon = assets.get('favicon') or company_logo
        report_logo = assets.get('report_logo') or company_logo

        logo_for_company = report_logo or company_logo

        companies = self.env['res.company'].sudo().search([])
        for company in companies:
            vals = {}
            if 'uses_default_logo' in company._fields:
                vals['uses_default_logo'] = False
            if logo_for_company:
                # company.logo is used on invoices, quotations, and PDF reports
                vals['logo'] = logo_for_company
            company.write(vals)
            _logger.info('Applied company logo on %s', company.display_name)

        websites = self.env['website'].sudo().search([])
        for website in websites:
            wvals = {}
            if website_logo:
                wvals['logo'] = website_logo
                if 'social_default_image' in website._fields:
                    wvals['social_default_image'] = website_logo
            if favicon:
                wvals['favicon'] = favicon
            if wvals:
                website.write(wvals)
                if hasattr(website, 'clear_cache'):
                    website.clear_cache()
                _logger.info('Applied website branding on %s', website.name)

        return True

    @api.model
    def _load_branding_assets(self):
        """Load branding binaries from static/branding (preferred) or legacy folders."""
        branding_dir = self._branding_directory()
        if not branding_dir:
            return {}

        mapping = {
            'company_logo': [
                'company_logo.png',
                'Havano Companay Logo.png',
                'havano_logo.png',
            ],
            'website_logo': [
                'website_logo.png',
                'Havano website header trans.png',
                'Havano website header.png',
            ],
            'favicon': [
                'favicon.ico',
                'favicon trans.png',
                'favicon.png',
            ],
            'report_logo': [
                'report_logo.png',
                'Havano report head logo trans.png',
                'Havano report head logo.png',
            ],
        }

        assets = {}
        for key, filenames in mapping.items():
            for filename in filenames:
                path = branding_dir / filename
                if path.is_file():
                    assets[key] = self._read_file_b64(path)
                    _logger.info('Loaded branding asset %s from %s', key, path)
                    break
        return assets

    @api.model
    def _branding_directory(self):
        module_path = get_module_path('ace_remove_website_powered_by_odoo')
        if not module_path:
            return None
        root = Path(module_path)
        for candidate in (
            root / 'static' / 'branding',
            root / 'havano branding',
            root / 'static' / 'description',
        ):
            if candidate.is_dir():
                return candidate
        return None

    @staticmethod
    def _read_file_b64(path):
        with open(path, 'rb') as handle:
            return base64.b64encode(handle.read())

    # -------------------------------------------------------------------------
    # Optional: copy images into other addon static paths (havano_branding/)
    # -------------------------------------------------------------------------

    @api.model
    def seed_branding_images(self):
        """Copy images from havano_branding/<module>/<path> into addon directories."""
        module_root = get_module_path('ace_remove_website_powered_by_odoo')
        if not module_root:
            _logger.warning('Cannot locate ace_remove_website_powered_by_odoo module path')
            return False

        source_root = Path(module_root) / 'havano_branding'
        if not source_root.exists():
            _logger.info('No havano_branding directory at %s (optional)', source_root)
            return True

        addon_roots = self._addons_roots()
        copied = skipped = failed = 0

        for src in source_root.rglob('*'):
            if not src.is_file() or src.suffix.lower() not in self.IMAGE_EXTENSIONS:
                continue
            rel_parts = src.relative_to(source_root).parts
            if len(rel_parts) < 2:
                skipped += 1
                continue
            module_name = rel_parts[0]
            target_rel = Path(*rel_parts[1:])
            destination = self._resolve_module_destination(module_name, target_rel, addon_roots)
            if not destination:
                skipped += 1
                continue
            try:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, destination)
                copied += 1
            except OSError as err:
                failed += 1
                _logger.error('Failed to copy %s -> %s: %s', src, destination, err)

        _logger.info(
            'Addon file seeding: copied=%s skipped=%s failed=%s', copied, skipped, failed
        )
        return failed == 0

    def _resolve_module_destination(self, module_name, target_rel, addon_roots):
        for root in addon_roots:
            module_path = root / module_name
            if module_path.is_dir():
                return module_path / target_rel
        return None

    def _addons_roots(self):
        addon_paths = config.get('addons_path') or []
        if isinstance(addon_paths, str):
            paths = [p.strip() for p in addon_paths.split(',') if p.strip()]
        else:
            paths = [str(p).strip() for p in addon_paths if str(p).strip()]
        return [Path(p) for p in paths]

    # -------------------------------------------------------------------------
    # Footer copyright
    # -------------------------------------------------------------------------

    @api.model
    def _patch_footer_copyright_view(self):
        """Ensure DB view arch uses Havano copyright (safety net beyond XML inherit)."""
        view = self.env.ref(
            'website.footer_copyright_company_name',
            raise_if_not_found=False,
        )
        if not view:
            return False
        arch = view.arch_db if isinstance(view.arch_db, str) else (
            view.arch_db.get('en_US') or next(iter(view.arch_db.values()), '')
        )
        if not arch or 'Company name' not in arch:
            return False
        new_arch = arch.replace('Company name', 'Havano')
        new_arch = new_arch.replace('Company Name', 'Havano')
        if isinstance(view.arch_db, dict):
            view.write({'arch_db': {lang: new_arch for lang in view.arch_db}})
        else:
            view.write({'arch_db': new_arch})
        _logger.info('Patched website footer copyright view to Havano')
        return True

    # -------------------------------------------------------------------------
    # Metadata / text rebranding
    # -------------------------------------------------------------------------

    @api.model
    def _rebrand_company_metadata(self):
        companies = self.env['res.company'].sudo().search([])
        for company in companies:
            vals = {}
            if company.name in {
                'My Company', 'YourCompany', 'My Company (San Francisco)', 'Company name',
            }:
                vals['name'] = 'Havano'
            if company.email in {'info@yourcompany.com', 'admin@yourcompany.com', 'info@yourcompany.example.com'}:
                vals['email'] = 'info@havano.com'
            if company.website in {'http://www.example.com', 'http://www.yourcompany.com'}:
                vals['website'] = 'https://www.havano.com'
            if vals:
                company.write(vals)

        websites = self.env['website'].sudo().search([])
        for website in websites:
            if website.name in {'My Website', 'YourCompany', 'Website'}:
                website.name = 'Havano'
        return True

    @api.model
    def _rebrand_email_templates(self):
        templates = self.env['mail.template'].sudo().search([])
        replacements = [
            ('Powered by Odoo', 'Powered by Havano'),
            ('Odoo', 'Havano'),
            ('odoo.com', 'havano.com'),
            ('www.odoo.com', 'www.havano.com'),
            ('YourCompany', 'Havano'),
            ('info@yourcompany.com', 'info@havano.com'),
            ('info@yourcompany.example.com', 'info@havano.com'),
            ('Company name', 'Havano'),
        ]
        updated = 0
        for template in templates:
            subject = template.subject or ''
            body = template.body_html or ''
            new_subject, new_body = subject, body
            changed = False
            for old, new in replacements:
                if old in new_subject:
                    new_subject = new_subject.replace(old, new)
                    changed = True
                if old in new_body:
                    new_body = new_body.replace(old, new)
                    changed = True
            if changed:
                template.write({'subject': new_subject, 'body_html': new_body})
                updated += 1
        _logger.info('Updated %s email templates', updated)
        return True

    @api.model
    def _rebrand_system_parameters(self):
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('web.base.name', 'Havano')
        params.set_param('web.base.company.name', 'Havano')
        params.set_param('ace_remove_website_powered_by_odoo.footer_copyright', HAVANO_COPYRIGHT)
        return True

    @api.model
    def _rebrand_portal(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'portal.footer_copyright', HAVANO_COPYRIGHT
        )
        return True

    def _notification(self, title, message):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'type': 'success',
                'sticky': False,
            },
        }
