// Havano Backend Branding
odoo.define('havano_branding.backend', function (require) {
    "use strict";
    
    var core = require('web.core');
    
    $(document).ready(function() {
        // Replace any remaining Odoo text
        $('*').each(function() {
            var $el = $(this);
            if ($el.contents().length === 0 && $el.text().indexOf('Odoo') !== -1) {
                var newText = $el.text().replace(/Odoo/g, 'Havano');
                if (newText !== $el.text()) {
                    $el.text(newText);
                }
            }
        });
        
        // Update page title if needed
        if (document.title.indexOf('Odoo') !== -1) {
            document.title = document.title.replace(/Odoo/g, 'Havano');
        }
    });
});