# -*- coding: utf-8 -*-
{
    'name': 'Purchase Request Approval by oki',
    'version': '1.0',
    'summary': 'Multi-level approval for purchase requests',
    'description': '''
        This module adds multi-level approval workflow to purchase requests:
        - Define multiple approval levels
        - Track approval history
        - Configurable approval hierarchy
    ''',
    'category': 'Purchase',
    'author': 'oki',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'purchase',
        'purchase_stock',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/purchase_request_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}