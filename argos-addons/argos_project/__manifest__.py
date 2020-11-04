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
    'sequence': -81,
    'depends': [
        'project',
        'mail',
        'industry_fsm',
        'argos_sale',
    ],
    'data': [
        'views/report_surgery.xml',
        'views/assets.xml',
        'views/mail_activity_views.xml',
        'views/mail_compose_message_views.xml',
        'views/project_task_views.xml',
    ],
    'qweb': [
        'static/src/xml/activity_dropdown.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
