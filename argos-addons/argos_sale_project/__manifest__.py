# -*- coding: utf-8 -*-
{
    'name': 'Argos Sale Project',
    'summary': '',
    'category': 'Sale and Project',
    'version': '1.0',
    'sequence': -82,
    'author': '',
    'license': 'AGPL-3',
    'website': 'https://arkeup.com',
    'description': '',
    'depends': [
        'argos_contact',
        'argos_purchase',
        'argos_sale',
        'project',
    ],
    'data': [
        # security
        'security/ir.model.access.csv',
        # views
        'views/maintenance_equipment_views.xml',
        'views/sale_order_views.xml',
        'views/project_task_line_views.xml',
        'views/project_task_views.xml',
        'views/res_partner_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
