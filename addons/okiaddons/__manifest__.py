# -*- coding: utf-8 -*-
{
    'name': 'Oki Addons',
    'version': '1.0',
    'summary': 'Custom module for business',
    'description': '''
        Custom module with the following features:
        - Customized Sales Order with Division
        - Customer Credit Limit per Division
        - Stock Inventory Report
    ''',
    'category': 'Sales',
    'author': 'Developer',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale_management',
        'sale_stock',
        'account',
        'stock',
        'contacts',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/division_data.xml',
        'views/division_views.xml',
        'views/res_partner_views.xml',
        'views/product_views.xml',
        'views/sale_order_views.xml',
        'views/res_config_settings_views.xml',
        'reports/stock_inventory_report_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}