# -*- coding: utf-8 -*-
{
    'name': 'Argos Sale',
    'summary': '',
    'category': 'Sale',
    'version': '1.0',
    'sequence': -83,
    'author': 'ArkeUp',
    'license': 'AGPL-3',
    'website': 'https://arkeup.com',
    'description': '',
    'depends': [
        'argos_contact',
        'sale_management',
        'sale_operating_unit',
        'argos_product',
        'sale_coupon',
        'sale_product_pack',
        'sale_product_configurator',
        'sale_order_line_sequence',
        'argos_hr',
    ],
    'data': [
        # security
        'security/ir.model.access.csv',
        # data
        'data/product_template_data.xml',
        'data/res_config_parameter_data.xml',
        'data/mail_template_data.xml',
        'data/server_ftp_data.xml',
        # views
        'views/sale_report_views.xml',
        'views/sale_order_refer_views.xml',
        'views/sale_order_line_views.xml',
        'views/sale_order_views.xml',
        'views/consultation_type_views.xml',
        'views/res_partner_views.xml',
        'views/product_template_views.xml',
        'views/assets.xml',
        'views/surveillance_certificate_report.xml',
        'views/report_certificate_transit.xml',
        # wizard views
        'views/wizard/api_information_wizard.xml',
    ],
    'qweb': ['static/src/xml/tooltips.xml'],
    'application': False,
    'installable': True,
    'auto_install': False,
}
