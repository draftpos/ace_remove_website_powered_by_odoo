# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    def write(self, vals):
        """Override to auto-rebrand when company is created"""
        res = super().write(vals)
        
        # If this is a new company being created, auto-rebrand it
        if vals.get('name') and vals['name'] in ['My Company', 'YourCompany']:
            self._auto_rebrand_company()
        
        return res
    
    def _auto_rebrand_company(self):
        """Auto-rebrand a new company to Havano"""
        self.write({
            'name': 'Havano',
            'email': 'info@havano.com',
            'website': 'https://www.havano.com',
            'email_secondary_color': '#667eea',
            'email_primary_color': '#ffffff',
        })