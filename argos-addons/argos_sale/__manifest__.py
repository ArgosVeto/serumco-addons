# -*- coding: utf-8 -*-
{
    'name': 'Argos Sale',
    'summary': '',
    'category': 'Sale',
    'version': '1.0',
    'sequence': -83,
    'author': 'ArkeUp',
    'license': 'AGPL-3',
    'website': 'https://arkeup.com',
    'description': '',
    'depends': [
        'argos_contact',
        'sale_management',
        'sale_operating_unit',
    ],
    'data': [
        # data
        'data/product_template_data.xml',
        'data/res_config_parameter_data.xml',
        # views
        'views/sale_order_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
