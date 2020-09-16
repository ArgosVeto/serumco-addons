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
        'security/ir.model.access.csv',
        'views/product_supplierinfo_views.xml',
        'views/product_template_views.xml',
        'views/product_attribute_views.xml',
        'views/product_category_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
