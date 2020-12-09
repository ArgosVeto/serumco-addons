# -*- coding: utf-8 -*-
{
    'name': 'Argos Account',
    'summary': '',
    'category': 'Account',
    'version': '1.0',
    'sequence': -88,
    'author': '',
    'license': 'AGPL-3',
    'website': 'https://arkeup.com',
    'description': '',
    'depends': [
        'argos_base',
        'account_payment',
        'account_accountant',
        'argos_operating_unit',
        'hr_expense',
    ],
    'data': [
        # data
        'data/mail_template_data.xml',
        # views
        'views/res_partner_views.xml',
        'views/res_bank_views.xml',
        'views/operating_unit_views.xml',
        'views/product_template_views.xml',
        'views/report_invoice_inherit.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
