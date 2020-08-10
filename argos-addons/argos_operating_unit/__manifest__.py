# -*- coding: utf-8 -*-
{
    'name': 'Argos Operating Unit',
    'summary': '',
    'category': 'Base',
    'version': '1.0',
    'sequence': -90,
    'author': 'ArkeUp',
    'license': 'AGPL-3',
    'website': 'https://arkeup.com',
    'description': '',
    'depends': [
        'argos_base',
        'operating_unit'
    ],
    'data': [
        # data
        # security
        'security/ir.model.access.csv',
        # views
        'views/res_partner_views.xml',
        'views/animal_animal_views.xml',
        'views/operating_unit_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
