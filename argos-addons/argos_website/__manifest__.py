# -*- coding: utf-8 -*-
{
    'name': 'Argos Website',
    'summary': '',
    'category': 'Website',
    'version': '1.0',
    'sequence': -94,
    'author': 'ArkeUp',
    'license': 'AGPL-3',
    'website': 'https://arkeup.com',
    'description': '',
    'depends': [
        'argos_product',
        'website_sale',
    ],
    'data': [
        # data
        # security
        'security/ir.model.access.csv',
        # views
        'views/product_template_view.xml',
        'views/templates_view.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}