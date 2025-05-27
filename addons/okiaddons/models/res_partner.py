# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartnerDivision(models.Model):
    _name = 'res.partner.division'
    _description = 'Partner Division'
    _rec_name = 'division_id'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True, ondelete='cascade')
    division_id = fields.Many2one('business.division', string='Division', required=True)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    credit_limit = fields.Float(string='Credit Limit', default=0.0)
    credit_used = fields.Float(string='Credit Used', compute='_compute_credit_used')
    credit_available = fields.Float(string='Credit Available', compute='_compute_credit_available')
    salesperson_id = fields.Many2one('res.users', string='Salesperson')
    
    @api.depends('partner_id', 'division_id')
    def _compute_credit_used(self):
        for record in self:
            # Calculate credit used from invoices for this partner and division
            invoices = self.env['account.move'].search([
                ('partner_id', '=', record.partner_id.id),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', 'not in', ['paid', 'reversed']),
                ('invoice_division_id', '=', record.division_id.id)
            ])
            record.credit_used = sum(invoices.mapped('amount_residual'))
    
    @api.depends('credit_limit', 'credit_used')
    def _compute_credit_available(self):
        for record in self:
            record.credit_available = record.credit_limit - record.credit_used

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    division_ids = fields.One2many('res.partner.division', 'partner_id', string='Divisions')
    
    def get_division_credit_info(self, division_id):
        division_info = self.division_ids.filtered(lambda d: d.division_id.id == division_id)
        if division_info:
            return {
                'credit_limit': division_info[0].credit_limit,
                'credit_used': division_info[0].credit_used,
                'credit_available': division_info[0].credit_available,
                'salesperson_id': division_info[0].salesperson_id.id,
                'pricelist_id': division_info[0].pricelist_id.id,
            }
        return {
            'credit_limit': 0.0,
            'credit_used': 0.0,
            'credit_available': 0.0,
            'salesperson_id': False,
            'pricelist_id': False,
        }