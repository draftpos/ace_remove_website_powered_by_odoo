# -*- coding: utf-8 -*-

from . import models
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def _auto_rebrand_to_havano(*args):
    """Post-init hook to automatically rebrand Odoo to Havano on module install"""
    if len(args) == 1:
        # Odoo versions that pass env directly
        env = args[0]
    elif len(args) == 2:
        # Odoo versions that pass cr, registry
        cr, _registry = args
        env = api.Environment(cr, SUPERUSER_ID, {})
    else:
        raise TypeError("_auto_rebrand_to_havano received unexpected arguments")

    try:
        _logger.info("=" * 60)
        _logger.info("STARTING HAVANO AUTO REBRANDING ON INSTALL")
        _logger.info("=" * 60)

        env['havano.rebranding'].sudo().run_full_seed()

        _logger.info("=" * 60)
        _logger.info("HAVANO AUTO REBRANDING COMPLETED SUCCESSFULLY")
        _logger.info("=" * 60)

    except Exception as e:
        _logger.error("Could not auto-rebrand: %s", str(e))
        import traceback
        _logger.error(traceback.format_exc())