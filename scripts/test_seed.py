env['havano.rebranding'].sudo().run_full_seed()
c = env.company
w = env['website'].search([], limit=1)
print('company_logo', bool(c.logo))
print('website_logo', bool(w.logo), 'favicon', bool(w.favicon), 'social', bool(w.social_default_image))
view = env.ref('website.footer_copyright_company_name')
arch = view.arch_db if isinstance(view.arch_db, str) else list(view.arch_db.values())[0]
print('footer_havano', 'Havano' in arch)
env.cr.commit()
