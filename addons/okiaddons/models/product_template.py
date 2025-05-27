# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    division_id = fields.Many2one('business.division', string='Division', index=True)
    take_in_plant_discount = fields.Float(string='Take in Plant Discount', help='Discount amount when pickup method is Take in Plant')