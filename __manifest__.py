# -*- coding: utf-8 -*-
{
    'name': 'Remove Powered by Odoo & Rebrand to Havano',
    'version': '19.0.2.1',
    'category': 'Website',
    'summary': 'Remove Odoo branding and automatically rebrand to Havano',
    'description': """
Remove Powered by Odoo & Rebrand to Havano
==========================================
This module automatically replaces all Odoo references with Havano upon installation.

**Features:**
- Automatically replaces "Powered by Odoo" with "Powered by Havano"
- Replaces all "Odoo" text with "Havano" everywhere
- Replaces Odoo.com links with Havano.com
- Updates company name to Havano
- Applies Havano logo automatically
- Rebrands email templates, portal, website footer
- No manual configuration needed - works on install
    """,
    'author': 'Havano / A Cloud ERP',
    'price': 10.00,
    'currency': "EUR",
    'website': 'https://www.havano.com',
    'depends': ['auth_signup', 'website', 'portal', 'sale', 'mail', 'base_setup'],
    'data': [
        'security/ir.model.access.csv',
        'data/rebranding_data.xml',  # NEW: Initial rebranding data
        'data/mail_template_data_portal_welcome.xml',
        'data/set_password_email.xml',
        'data/mail_template_user_signup_account_created.xml',
        'data/auth_signup_templates_email.xml',
        'data/digest_data.xml',
        'views/brand_promotion_message.xml',
        'views/portal_record_sidebar.xml',
 

    ],
    'assets': {
        'web.assets_backend': [
            'ace_remove_website_powered_by_odoo/static/description/havano.png',  # Add logo to assets
            'ace_remove_website_powered_by_odoo/static/src/js/backend_branding.js',
        ],
        'web.assets_frontend': [
            'ace_remove_website_powered_by_odoo/static/description/havano.png',  # Add logo to frontend assets
            'ace_remove_website_powered_by_odoo/static/src/scss/frontend_branding.scss',
        ],
    },
    'post_init_hook': '_auto_rebrand_to_havano',  # NEW: Auto rebrand on install
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
}