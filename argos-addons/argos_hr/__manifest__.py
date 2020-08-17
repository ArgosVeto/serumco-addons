# -*- coding: utf-8 -*-
{
    'name': 'Argos HR',
    'summary': '',
    'category': 'Employees',
    'version': '1.0',
    'sequence': -90,
    'author': 'ArkeUp',
    'license': 'AGPL-3',
    'website': 'https://arkeup.com',
    'description': '',
    'depends': [
        'argos_contact',
        'hr_skills',

    ],
    'data': [
        'views/hr_employee_views.xml',
        'views/hr_skills_views.xml',
        'views/res_partner_views.xml',
        'wizard/hr_departure_wizard_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
