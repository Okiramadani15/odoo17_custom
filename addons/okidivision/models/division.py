# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Division(models.Model):
    _name = 'business.division'
    _description = 'Business Division'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    active = fields.Boolean(default=True)
    
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'Division code must be unique!')
    ]
    
    def name_get(self):
        result = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            result.append((record.id, name))
        return result