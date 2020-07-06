# -*- coding: utf-8 -*-
{
    'name': 'Argos Planning',
    'summary': '',
    'category': 'Planning',
    'version': '1.0',
    'sequence': -96,
    'author': '',
    'license': 'AGPL-3',
    'website': 'https://arkeup.com',
    'description': '',
    'depends': [
        'argos_base',
        'planning',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/planning_role_data.xml',
        'views/consultation_views.xml',
        'views/planning_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}