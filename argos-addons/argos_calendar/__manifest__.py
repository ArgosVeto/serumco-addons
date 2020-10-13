# -*- coding: utf-8 -*-
{
    'name': 'Argos Calendar',
    'summary': '',
    'category': 'Calendar',
    'version': '1.0',
    'sequence': -98,
    'author': 'Omar OUHARI',
    'license': 'AGPL-3',
    'website': 'https://arkeup.com',
    'description': '',
    'depends': [
        'calendar',
        'argos_base',
        'argos_planning',
        'argos_planning_sale',
    ],
    'data': [
        'views/calendar_templates.xml',
        'views/calendar_views.xml',
    ],
    'qweb': [
        "static/src/xml/web_calendar.xml",
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
