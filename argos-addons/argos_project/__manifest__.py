# -*- coding: utf-8 -*-
{
    'name': 'Argos Project',
    'summary': '',
    'category': 'Operations/Project',
    'version': '1.0',
    'author': 'ArkeUp',
    'license': 'AGPL-3',
    'website': 'https://arkeup.com',
    'description': '',
    'depends': [
        'argos_base',
        'project',
        'mail',
        'industry_fsm',
        'sale',
    ],
    'data': [
        'views/assets.xml',
        'views/mail_activity_views.xml',
    ],
    'qweb': [
        'static/src/xml/activity_dropdown.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
