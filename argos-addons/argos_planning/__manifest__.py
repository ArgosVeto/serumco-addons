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
        'argos_contact',
        'planning',
        'argos_account',
        'argos_sale',
    ],
    'data': [
        # data
        'data/mail_template_data.xml',
        'data/planning_role_data.xml',
        'data/planning_cron.xml',
        'data/cancel_mail_template_data.xml',
        'data/welcome_mail_template_data.xml',
        'data/review_mail_template_data.xml',
        # security
        'security/ir.model.access.csv',
        'security/res_users_groups.xml',
        # views
        'views/planning_views.xml',
        'views/assignment_views.xml',
        'views/res_partner_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
