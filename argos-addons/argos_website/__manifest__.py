# -*- coding: utf-8 -*-
{
    'name': 'Argos Website',
    'summary': '',
    'category': 'Website',
    'version': '1.0',
    'sequence': -94,
    'author': 'ArkeUp',
    'license': 'AGPL-3',
    'website': 'https://arkeup.com',
    'description': '',
    'depends': [
        'argos_product',
        'website_sale',
        'website_hr_recruitment',
        'website_blog',
        'website_forum',
        'website_helpdesk',
        'payment_stripe',
        'website_sale_coupon',
        'jitsi_meet_integration',
    ],
    'data': [
        # data
        'data/res_config_settings.xml',
        # security
        'security/ir.model.access.csv',
        # views
        'views/product_template_view.xml',
        'views/templates_view.xml',
        'views/product_attribute_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}