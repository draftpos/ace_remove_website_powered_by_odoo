# -*- coding: utf-8 -*-

from odoo import models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def action_seed_havano_branding(self):
        """Seed Havano logos, favicon, footer copyright, and related branding."""
        self.env['havano.rebranding'].sudo().run_full_seed()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Havano Branding'),
                'message': _(
                    'Havano branding has been applied: company logo, website logo, '
                    'favicon, social share image, footer copyright, and reports.'
                ),
                'type': 'success',
                'sticky': False,
            },
        }
