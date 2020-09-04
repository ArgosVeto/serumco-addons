# -*- coding: utf-8 -*-
{
    'name': 'Argos Purchase',
    'summary': '',
    'category': 'Purchase',
    'version': '1.0',
    'sequence': -83,
    'author': 'ArkeUp',
    'license': 'AGPL-3',
    'website': 'https://arkeup.com',
    'description': '',
    'depends': [
        'argos_base',
        'purchase_requisition',
        'purchase_operating_unit',
    ],
    'data': [
        'views/res_partner_views.xml',
        'views/product_template_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
