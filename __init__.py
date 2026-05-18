# -*- coding: utf-8 -*-

from . import models
import logging

_logger = logging.getLogger(__name__)

def _auto_rebrand_to_havano(env):
    """Post-init hook to automatically rebrand Odoo to Havano on module install"""
    
    try:
        _logger.info("=" * 60)
        _logger.info("STARTING HAVANO AUTO REBRANDING ON INSTALL")
        _logger.info("=" * 60)
        
        # Run rebranding
        env['havano.rebranding'].sudo().auto_rebrand()
        
        _logger.info("=" * 60)
        _logger.info("HAVANO AUTO REBRANDING COMPLETED SUCCESSFULLY")
        _logger.info("=" * 60)
        
    except Exception as e:
        _logger.error("Could not auto-rebrand: %s", str(e))
        import traceback
        _logger.error(traceback.format_exc())