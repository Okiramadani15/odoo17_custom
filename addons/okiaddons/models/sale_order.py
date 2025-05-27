# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    division_id = fields.Many2one('business.division', string='Division')
    pickup_method = fields.Selection([
        ('delivery', 'Delivery'),
        ('take_in_plant', 'Take in Plant')
    ], string='Pickup Method', default='delivery')
    expiration_date = fields.Date(string='Expiration Date')
    is_credit_limit_exceeded = fields.Boolean(string='Credit Limit Exceeded', compute='_compute_is_credit_limit_exceeded', store=True)
    has_overdue_invoices = fields.Boolean(string='Has Overdue Invoices', compute='_compute_has_overdue_invoices', store=True)
    
    @api.onchange('division_id')
    def _onchange_division_id(self):
        # Clear partner when division changes
        self.partner_id = False
        # Set domain for partner_id based on division
        if self.division_id:
            return {'domain': {'partner_id': [('division_ids.division_id', '=', self.division_id.id)]}}
        return {'domain': {'partner_id': []}}
    
    @api.onchange('partner_id', 'division_id')
    def _onchange_partner_division(self):
        if self.partner_id and self.division_id:
            division_info = self.partner_id.get_division_credit_info(self.division_id.id)
            self.pricelist_id = division_info.get('pricelist_id')
            self.user_id = division_info.get('salesperson_id')
            
            # Check for overdue invoices
            overdue_invoices = self.env['account.move'].search([
                ('partner_id', '=', self.partner_id.id),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', 'not in', ['paid', 'reversed']),
                ('invoice_date_due', '<', fields.Date.today())
            ])
            
            if overdue_invoices:
                return {
                    'warning': {
                        'title': _('Warning!'),
                        'message': _('This customer has overdue invoices.')
                    }
                }
    
    @api.depends('partner_id', 'division_id', 'amount_total')
    def _compute_is_credit_limit_exceeded(self):
        for order in self:
            if order.partner_id and order.division_id:
                division_info = order.partner_id.get_division_credit_info(order.division_id.id)
                credit_available = division_info.get('credit_available', 0.0)
                order.is_credit_limit_exceeded = (credit_available < order.amount_total)
            else:
                order.is_credit_limit_exceeded = False
    
    @api.depends('partner_id')
    def _compute_has_overdue_invoices(self):
        for order in self:
            if order.partner_id:
                overdue_invoices = self.env['account.move'].search([
                    ('partner_id', '=', order.partner_id.id),
                    ('move_type', '=', 'out_invoice'),
                    ('state', '=', 'posted'),
                    ('payment_state', 'not in', ['paid', 'reversed']),
                    ('invoice_date_due', '<', fields.Date.today())
                ], limit=1)
                order.has_overdue_invoices = bool(overdue_invoices)
            else:
                order.has_overdue_invoices = False
    
    def action_confirm(self):
        for order in self:
            warning_messages = []
            
            if order.is_credit_limit_exceeded:
                warning_messages.append(_('This customer has exceeded their credit limit for this division.'))
            
            if order.has_overdue_invoices:
                warning_messages.append(_('This customer has overdue invoices.'))
            
            if warning_messages:
                message = '\n'.join(warning_messages)
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Warning'),
                    'res_model': 'warning.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_message': message,
                        'default_sale_order_id': order.id
                    }
                }
        
        return super(SaleOrder, self).action_confirm()

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        
        if self.product_id and self.order_id.pickup_method == 'take_in_plant' and self.product_id.take_in_plant_discount > 0:
            self.price_unit = self.price_unit - self.product_id.take_in_plant_discount
        
        return result
    
    @api.onchange('product_id')
    def _onchange_product_id_check_division(self):
        if self.product_id and self.order_id.division_id and self.product_id.division_id != self.order_id.division_id:
            return {
                'warning': {
                    'title': _('Warning!'),
                    'message': _('This product does not belong to the selected division.')
                }
            }

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    invoice_division_id = fields.Many2one('business.division', string='Division')

class WarningWizard(models.TransientModel):
    _name = 'warning.wizard'
    _description = 'Warning Wizard'
    
    message = fields.Text(string='Message')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    
    def action_confirm_anyway(self):
        if self.sale_order_id:
            return self.sale_order_id.with_context(bypass_warning=True).action_confirm()
        return {'type': 'ir.actions.act_window_close'}