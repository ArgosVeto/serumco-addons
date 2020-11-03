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
        'argos_contact',
        'operating_unit'
    ],
    'data': [
        # data
        'data/sequence_data.xml',
        'data/res_config_parameter_data.xml',
        # security
        'security/ir.model.access.csv',
        # views
        'views/res_partner_views.xml',
        'views/operating_unit_views.xml',
        'views/operating_unit_room_views.xml',
        'views/operating_unit_certification_views.xml',
        'views/operating_unit_service_views.xml',
        'views/operating_unit_templates.xml',
    ],
    'qweb': [
        "static/src/xml/operating_unit.xml",
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
