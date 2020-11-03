# -*- coding: utf-8 -*-
{
    'name': 'Argos Planning Sale',
    'summary': '',
    'category': 'Planning and Sale',
    'version': '1.0',
    'sequence': -83,
    'author': '',
    'license': 'AGPL-3',
    'website': 'https://arkeup.com',
    'description': '',
    'depends': [
        'argos_contact',
        'argos_planning',
        'argos_sale',
    ],
    'data': [
        # views
        'views/planning_slot_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
