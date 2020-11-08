# -*- coding: utf-8 -*-
{
    'name': 'Argos Contact',
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
        'partner_contact_gender',
        'partner_contact_birthdate',
    ],
    'data': [
        # data
        # security
        'security/ir.model.access.csv',
        # views
        'views/res_partner_parameter_views.xml',
        'views/res_partner_category_views.xml',
        'views/res_partner_weight_views.xml',
        'views/res_partner_views.xml',
        'views/res_partner_pathology_views.xml',
        'views/passport_passport_views.xml',
        'views/menu_views.xml',
        'views/template_report.xml',
        'views/export_medical_history_views.xml'
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
