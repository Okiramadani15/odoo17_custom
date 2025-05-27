# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class ApprovalLevel(models.Model):
    _name = 'approval.level'
    _description = 'Approval Level'
    _order = 'sequence'

    name = fields.Char('Name', required=True)
    sequence = fields.Integer('Sequence', default=10)
    user_ids = fields.Many2many('res.users', string='Approvers')
    min_amount = fields.Float('Minimum Amount', default=0.0)
    max_amount = fields.Float('Maximum Amount')
    active = fields.Boolean(default=True)

class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _description = 'Purchase Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char('Request Reference', required=True, copy=False, readonly=True, 
                      default=lambda self: _('New'))
    date_request = fields.Date('Request Date', default=fields.Date.context_today, required=True)
    requested_by = fields.Many2one('res.users', 'Requested By', required=True,
                                  default=lambda self: self.env.user)
    department_id = fields.Many2one('hr.department', 'Department')
    company_id = fields.Many2one('res.company', 'Company', required=True, 
                                default=lambda self: self.env.company)
    line_ids = fields.One2many('purchase.request.line', 'request_id', 'Products')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('done', 'Done')
    ], string='Status', default='draft', tracking=True)
    
    total_amount = fields.Float('Total Amount', compute='_compute_total_amount', store=True)
    current_approval_level = fields.Integer('Current Approval Level', default=0)
    approval_history_ids = fields.One2many('purchase.request.approval.history', 'request_id', 'Approval History')
    
    @api.depends('line_ids.estimated_cost', 'line_ids.quantity')
    def _compute_total_amount(self):
        for request in self:
            request.total_amount = sum(line.estimated_cost * line.quantity for line in request.line_ids)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.request') or _('New')
        return super(PurchaseRequest, self).create(vals_list)
    
    def action_submit_for_approval(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_('You cannot submit an empty purchase request.'))
        self.state = 'to_approve'
        self._create_approval_levels()
        return True
    
    def _create_approval_levels(self):
        self.ensure_one()
        # Find applicable approval levels based on amount
        approval_levels = self.env['approval.level'].search([
            ('min_amount', '<=', self.total_amount),
            '|', ('max_amount', '>=', self.total_amount), ('max_amount', '=', 0)
        ], order='sequence')
        
        if not approval_levels:
            raise UserError(_('No approval levels configured for this amount.'))
        
        # Reset current level
        self.current_approval_level = 0
        
        # Create approval history entries
        for level in approval_levels:
            for user in level.user_ids:
                self.env['purchase.request.approval.history'].create({
                    'request_id': self.id,
                    'level_id': level.id,
                    'user_id': user.id,
                    'status': 'pending'
                })
        
        # Notify first level approvers
        self._notify_next_approvers()
    
    def _notify_next_approvers(self):
        self.ensure_one()
        next_level = self.current_approval_level + 1
        next_approvals = self.approval_history_ids.filtered(
            lambda a: a.level_id.sequence == next_level and a.status == 'pending')
        
        if next_approvals:
            # Create activity for next approvers
            for approval in next_approvals:
                self.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=approval.user_id.id,
                    note=_('Purchase request %s requires your approval') % self.name
                )
    
    def action_approve(self):
        self.ensure_one()
        current_user = self.env.user
        
        # Find current user's pending approval
        current_approval = self.approval_history_ids.filtered(
            lambda a: a.user_id == current_user and a.status == 'pending')
        
        if not current_approval:
            raise UserError(_('You are not authorized to approve this request.'))
        
        # Mark as approved
        current_approval.write({
            'status': 'approved',
            'date': fields.Datetime.now()
        })
        
        # Check if all approvals at this level are done
        current_level = current_approval.level_id.sequence
        level_approvals = self.approval_history_ids.filtered(
            lambda a: a.level_id.sequence == current_level)
        
        all_approved = all(a.status == 'approved' for a in level_approvals)
        
        if all_approved:
            # Move to next level
            self.current_approval_level = current_level
            
            # Check if this was the last level
            next_approvals = self.approval_history_ids.filtered(
                lambda a: a.level_id.sequence > current_level and a.status == 'pending')
            
            if not next_approvals:
                # Final approval
                self.state = 'approved'
                self.message_post(body=_('Purchase request has been fully approved.'))
            else:
                # Notify next level
                self._notify_next_approvers()
        
        return True
    
    def action_reject(self):
        self.ensure_one()
        current_user = self.env.user
        
        # Find current user's pending approval
        current_approval = self.approval_history_ids.filtered(
            lambda a: a.user_id == current_user and a.status == 'pending')
        
        if not current_approval:
            raise UserError(_('You are not authorized to reject this request.'))
        
        # Mark as rejected
        current_approval.write({
            'status': 'rejected',
            'date': fields.Datetime.now()
        })
        
        # Reject the whole request
        self.state = 'rejected'
        self.message_post(body=_('Purchase request has been rejected.'))
        
        return True
    
    def action_reset_to_draft(self):
        self.ensure_one()
        if self.state in ['rejected', 'to_approve']:
            # Delete approval history
            self.approval_history_ids.unlink()
            self.state = 'draft'
        return True
    
    def action_create_purchase_orders(self):
        self.ensure_one()
        if self.state != 'approved':
            raise UserError(_('You can only create purchase orders from approved requests.'))
        
        # Logic to create purchase orders would go here
        self.state = 'done'
        return True

class PurchaseRequestLine(models.Model):
    _name = 'purchase.request.line'
    _description = 'Purchase Request Line'
    
    request_id = fields.Many2one('purchase.request', 'Purchase Request', ondelete='cascade')
    product_id = fields.Many2one('product.product', 'Product', required=True)
    description = fields.Text('Description')
    quantity = fields.Float('Quantity', default=1.0, required=True)
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure', required=True)
    estimated_cost = fields.Float('Estimated Cost', required=True)
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.name
            self.uom_id = self.product_id.uom_id.id
            self.estimated_cost = self.product_id.standard_price

class PurchaseRequestApprovalHistory(models.Model):
    _name = 'purchase.request.approval.history'
    _description = 'Purchase Request Approval History'
    _order = 'level_id, id'
    
    request_id = fields.Many2one('purchase.request', 'Purchase Request', ondelete='cascade')
    level_id = fields.Many2one('approval.level', 'Approval Level')
    user_id = fields.Many2one('res.users', 'Approver')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='pending')
    date = fields.Datetime('Approval Date')
    
    def name_get(self):
        result = []
        for record in self:
            name = '%s - %s - %s' % (record.level_id.name, record.user_id.name, record.status)
            result.append((record.id, name))
        return result