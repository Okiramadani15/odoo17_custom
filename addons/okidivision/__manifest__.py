# -*- coding: utf-8 -*-
{
    'name': 'Oki Division',
    'version': '1.0',
    'summary': 'Division Management for Sales',
    'description': '''
        This module provides division management functionality for sales:
        - Create and manage business divisions
        - Configure divisions in sales settings
    ''',
    'category': 'Sales',
    'author': 'Developer',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale_management',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/division_views.xml',
        'data/division_data.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}