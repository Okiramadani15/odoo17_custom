# -*- coding: utf-8 -*-
from . import models
from . import reports

from odoo import api, SUPERUSER_ID

def _post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Ensure divisions are properly set up
    divisions = env['business.division'].search([])
    if not divisions:
        # Create default divisions if not already created by XML data
        env['business.division'].create([
            {'name': 'SanQua', 'code': 'SQA'},
            {'name': 'Galon', 'code': 'GLN'},
            {'name': 'Batavia', 'code': 'BTV'},
            {'name': 'Beverage', 'code': 'BVG'}
        ])
    
    # Update existing products to use divisions
    products = env['product.template'].search([('division_id', '=', False)], limit=100)
    if products:
        # Assign default division to products without division
        default_division = env['business.division'].search([], limit=1)
        if default_division:
            products.write({'division_id': default_division.id})
            
    # Ensure sales menu items are properly set up
    menu = env['ir.ui.menu'].search([('name', '=', 'Divisions')])
    if menu and not menu.parent_id:
        config_menu = env.ref('sale.menu_sale_config', False)
        if config_menu:
            menu.write({'parent_id': config_menu.id})