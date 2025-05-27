# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
from datetime import datetime, timedelta

class StockInventoryReport(models.Model):
    _name = 'stock.inventory.report'
    _description = 'Stock Inventory Report'
    _auto = False
    
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_code = fields.Char(string='Product Code', readonly=True)
    product_name = fields.Char(string='Product Name', readonly=True)
    initial_qty = fields.Float(string='Initial Quantity', readonly=True)
    in_qty = fields.Float(string='In Quantity', readonly=True)
    out_qty = fields.Float(string='Out Quantity', readonly=True)
    final_qty = fields.Float(string='Final Quantity', readonly=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    location_id = fields.Many2one('stock.location', string='Location', readonly=True)
    date = fields.Date(string='Date', readonly=True)
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
            CREATE OR REPLACE VIEW %s AS (
                WITH stock_moves AS (
                    SELECT
                        sm.id,
                        sm.product_id,
                        sm.company_id,
                        sm.location_id,
                        sm.location_dest_id,
                        sm.product_uom_qty,
                        sm.product_uom,
                        sm.date::date as date
                    FROM
                        stock_move sm
                    WHERE
                        sm.state = 'done'
                )
                SELECT
                    row_number() OVER () as id,
                    p.id as product_id,
                    p.default_code as product_code,
                    p.name as product_name,
                    u.id as uom_id,
                    sm.date as date,
                    sm.company_id as company_id,
                    CASE
                        WHEN sm.location_id NOT IN (SELECT id FROM stock_location WHERE usage = 'internal')
                        AND sm.location_dest_id IN (SELECT id FROM stock_location WHERE usage = 'internal')
                        THEN sm.location_dest_id
                        ELSE sm.location_id
                    END as location_id,
                    0 as initial_qty,
                    CASE
                        WHEN sm.location_id NOT IN (SELECT id FROM stock_location WHERE usage = 'internal')
                        AND sm.location_dest_id IN (SELECT id FROM stock_location WHERE usage = 'internal')
                        THEN sm.product_uom_qty
                        ELSE 0
                    END as in_qty,
                    CASE
                        WHEN sm.location_id IN (SELECT id FROM stock_location WHERE usage = 'internal')
                        AND sm.location_dest_id NOT IN (SELECT id FROM stock_location WHERE usage = 'internal')
                        THEN sm.product_uom_qty
                        ELSE 0
                    END as out_qty,
                    0 as final_qty
                FROM
                    stock_moves sm
                JOIN
                    product_product p ON sm.product_id = p.id
                JOIN
                    product_template pt ON p.product_tmpl_id = pt.id
                JOIN
                    uom_uom u ON pt.uom_id = u.id
            )
        ''' % self._table)

class StockInventoryReportWizard(models.TransientModel):
    _name = 'stock.inventory.report.wizard'
    _description = 'Stock Inventory Report Wizard'
    
    start_date = fields.Date(string='Start Date', required=True, default=fields.Date.context_today)
    end_date = fields.Date(string='End Date', required=True, default=fields.Date.context_today)
    location_ids = fields.Many2many('stock.location', string='Locations', domain=[('usage', '=', 'internal')])
    
    def action_generate_report(self):
        self.ensure_one()
        
        # Delete old report lines
        self.env['stock.inventory.report.line'].search([]).unlink()
        
        # Calculate day before start date for initial balance
        day_before_start = self.start_date - timedelta(days=1)
        
        # Build domain for location filter
        domain = []
        if self.location_ids:
            domain.append(('location_id', 'in', self.location_ids.ids))
        
        # Get all products that have movements
        products = self.env['product.product'].search([])
        
        # Process each product
        for product in products:
            for location in self.location_ids or self.env['stock.location'].search([('usage', '=', 'internal')]):
                # Get initial quantity
                initial_qty = self.env['stock.quant']._get_available_quantity(
                    product, location, lot_id=None, package_id=None, owner_id=None, strict=False,
                    allow_negative=True, date=day_before_start
                )
                
                # Get incoming quantity during period
                in_domain = domain + [
                    ('product_id', '=', product.id),
                    ('location_id.usage', '!=', 'internal'),
                    ('location_dest_id', '=', location.id),
                    ('state', '=', 'done'),
                    ('date', '>=', self.start_date),
                    ('date', '<=', self.end_date)
                ]
                in_moves = self.env['stock.move'].search(in_domain)
                in_qty = sum(in_moves.mapped('product_uom_qty'))
                
                # Get outgoing quantity during period
                out_domain = domain + [
                    ('product_id', '=', product.id),
                    ('location_id', '=', location.id),
                    ('location_dest_id.usage', '!=', 'internal'),
                    ('state', '=', 'done'),
                    ('date', '>=', self.start_date),
                    ('date', '<=', self.end_date)
                ]
                out_moves = self.env['stock.move'].search(out_domain)
                out_qty = sum(out_moves.mapped('product_uom_qty'))
                
                # Calculate final quantity
                final_qty = initial_qty + in_qty - out_qty
                
                # Only create report line if there's movement or stock
                if initial_qty != 0 or in_qty != 0 or out_qty != 0 or final_qty != 0:
                    self.env['stock.inventory.report.line'].create({
                        'product_id': product.id,
                        'product_code': product.default_code or '',
                        'product_name': product.name,
                        'initial_qty': initial_qty,
                        'in_qty': in_qty,
                        'out_qty': out_qty,
                        'final_qty': final_qty,
                        'uom_id': product.uom_id.id,
                        'location_id': location.id,
                    })
        
        # Return action to show report
        return {
            'name': _('Stock Inventory Report'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.inventory.report.line',
            'view_mode': 'tree,form',
            'context': {'create': False},
        }

class StockInventoryReportLine(models.TransientModel):
    _name = 'stock.inventory.report.line'
    _description = 'Stock Inventory Report Line'
    
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_code = fields.Char(string='Product Code', readonly=True)
    product_name = fields.Char(string='Product Name', readonly=True)
    initial_qty = fields.Float(string='Initial Quantity', readonly=True)
    in_qty = fields.Float(string='In Quantity', readonly=True)
    out_qty = fields.Float(string='Out Quantity', readonly=True)
    final_qty = fields.Float(string='Final Quantity', readonly=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', readonly=True)
    location_id = fields.Many2one('stock.location', string='Location', readonly=True)