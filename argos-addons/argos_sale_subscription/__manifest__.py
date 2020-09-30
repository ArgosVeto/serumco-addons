# -*- coding: utf-8 -*-
{
    'name': 'Argos Sale Subscription',
    'summary': '',
    'category': 'Sales/Subscription',
    'version': '1.0',
    'sequence': -93,
    'author': 'ArkeUp',
    'license': 'AGPL-3',
    'website': 'https://arkeup.com',
    'description': '',
    'depends': [
        'argos_contact',
        'sale_subscription',
    ],
    'data': [
        'views/sale_subscription_views.xml',
        'views/res_partner_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
