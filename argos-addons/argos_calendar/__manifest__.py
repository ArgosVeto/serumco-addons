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
        'website_calendar',
        'project',
        'argos_base',
        'argos_planning',
        'argos_planning_sale',
    ],
    'data': [
        'views/calendar_templates.xml',
        'views/calendar_views.xml',
        'views/res_config_settings_views.xml',
        'views/website_calendar_templates.xml',
        'views/calendar_appointment_views.xml',
    ],
    'qweb': [
        "static/src/xml/web_calendar.xml",
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
