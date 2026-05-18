# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
import base64
import logging

_logger = logging.getLogger(__name__)


class HavanoRebranding(models.TransientModel):
    """Automatic rebranding to Havano"""
    _name = 'havano.rebranding'
    _description = 'Havano Auto Rebranding'

    @api.model
    def auto_rebrand(self):
        """Automatically rebrand everything to Havano on module install"""
        _logger.info("=" * 60)
        _logger.info("STARTING HAVANO AUTO REBRANDING")
        _logger.info("=" * 60)
        
        # 1. Update Company
        self._rebrand_company()
        
        # 2. Update Website (Configuration Settings)
        self._rebrand_website()
        
        # 3. Update Email Templates
        self._rebrand_email_templates()
        
        # 4. Update System Parameters
        self._rebrand_system_parameters()
        
        # 5. Update Portal Settings
        self._rebrand_portal()
        
        _logger.info("=" * 60)
        _logger.info("HAVANO AUTO REBRANDING COMPLETED")
        _logger.info("=" * 60)
        
        return True
    
    def _get_logo_data(self):
        """Get logo data from module"""
        logo_paths = [
            '/mnt/extra-addons/ace_remove_website_powered_by_odoo/static/description/havano.png',
            '/mnt/extra-addons/ace_remove_website_powered_by_odoo/static/description/havano_logo.png',
            '/mnt/extra-addons/havano_odoo_api/static/description/icon.png',
        ]
        
        for path in logo_paths:
            try:
                with open(path, 'rb') as f:
                    logo_data = base64.b64encode(f.read())
                    _logger.info(f"✓ Loaded logo from: {path}")
                    return logo_data
            except Exception:
                continue
        
        _logger.warning("No logo file found, using default")
        return None
    
    def _rebrand_company(self):
        """Rebrand company name, logo and settings"""
        Company = self.env['res.company']
        companies = Company.search([])
        
        logo_data = self._get_logo_data()
        
        for company in companies:
            # Update company name
            if company.name in ['My Company', 'YourCompany', 'My Company (San Francisco)']:
                company.write({'name': 'Havano'})
                _logger.info("✓ Updated company name to: Havano")
            
            # Update company email
            if company.email in ['info@yourcompany.com', 'admin@yourcompany.com']:
                company.write({'email': 'info@havano.com'})
                _logger.info("✓ Updated company email to: info@havano.com")
            
            # Update company website
            if company.website in ['http://www.example.com', 'http://www.yourcompany.com']:
                company.write({'website': 'https://www.havano.com'})
                _logger.info("✓ Updated company website to: https://www.havano.com")
            
            # Update company phone
            if company.phone in ['+1 650-123-4567', '+1 555-555-5556']:
                company.write({'phone': '+1 888-HAVANO-1'})
                _logger.info("✓ Updated company phone")
            
            # Update company logo_web (this is the main company logo)
            if logo_data:
                company.write({
                    'logo_web': logo_data,
                    'uses_default_logo': False,
                })
                _logger.info("✓ Updated company logo_web")
            
            # Update brand colors
            company.write({
                'email_secondary_color': '#667eea',
                'email_primary_color': '#ffffff',
            })
            _logger.info("✓ Updated brand colors to Havano theme")
        
        return True
    
    def _rebrand_website(self):
        """Update website configuration settings - THIS IS WHERE THE WEBSITE LOGO IS SET"""
        Website = self.env['website']
        websites = Website.search([])
        
        logo_data = self._get_logo_data()
        
        for website in websites:
            # Update website name
            if website.name in ['My Website', 'YourCompany', 'Website']:
                website.write({'name': 'Havano'})
                _logger.info("✓ Updated website name to: Havano")
            
            # Update website logo - THIS IS THE KEY FIX!
            if logo_data:
                website.write({
                    'logo': logo_data,  # This is the website logo field
                })
                _logger.info("✓ Updated website logo (Website → Configuration → Settings)")
            
            # Also update social default image
            if logo_data:
                website.write({'social_default_image': logo_data})
                _logger.info("✓ Updated social default image")
            
            # Update company relationship
            if website.company_id:
                website.company_id.write({'name': 'Havano'})
            
            # Clear website cache
            website.clear_cache()
            _logger.info("✓ Cleared website cache")
        
        return True
    
    def _rebrand_email_templates(self):
        """Rebrand all email templates - replace Odoo with Havano"""
        EmailTemplate = self.env['mail.template']
        
        templates = EmailTemplate.search([])
        replacements = [
            ('Odoo', 'Havano'),
            ('Powered by Odoo', 'Powered by Havano'),
            ('odoo.com', 'havano.com'),
            ('www.odoo.com', 'www.havano.com'),
            ('YourCompany', 'Havano'),
            ('info@yourcompany.com', 'info@havano.com'),
        ]
        
        updated_count = 0
        for template in templates:
            updated = False
            subject = template.subject or ''
            body = template.body_html or ''
            
            for old, new in replacements:
                if old in subject:
                    subject = subject.replace(old, new)
                    updated = True
                if old in body:
                    body = body.replace(old, new)
                    updated = True
            
            if updated:
                template.write({
                    'subject': subject,
                    'body_html': body,
                })
                updated_count += 1
        
        _logger.info("✓ Updated %s email templates", updated_count)
        return True
    
    def _rebrand_system_parameters(self):
        """Update system parameters"""
        ConfigParam = self.env['ir.config_parameter']
        
        # Set company name parameters
        ConfigParam.set_param('web.base.name', 'Havano')
        ConfigParam.set_param('web.base.company.name', 'Havano')
        
        _logger.info("✓ Updated system parameters")
        return True
    
    def _rebrand_portal(self):
        """Update portal settings"""
        # Update portal footer text
        ConfigParam = self.env['ir.config_parameter']
        ConfigParam.set_param('portal.footer_copyright', 'Havano')
        
        return True