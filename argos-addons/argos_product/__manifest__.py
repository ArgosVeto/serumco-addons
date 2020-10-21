# -*- coding: utf-8 -*-
{
    'name': 'Argos Product',
    'summary': '',
    'category': 'Product',
    'version': '1.0',
    'sequence': -90,
    'author': '',
    'license': 'AGPL-3',
    'website': 'https://arkeup.com',
    'description': '',
    'depends': [
        'argos_contact',
    ],
    'data': [
        # data
        'data/product_approval_data.xml',
        'data/product_template_data.xml',
        # security
        'security/ir.model.access.csv',
        # views
        'views/product_supplierinfo_views.xml',
        'views/product_template_views.xml',
        'views/product_attribute_views.xml',
        'views/product_category_views.xml',
        'views/product_route_views.xml',
        'views/product_documentation_views.xml',
        'views/product_approval_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
