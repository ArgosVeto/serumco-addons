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
        'website_rating',
    ],
    'data': [
        # data
        'data/mail_template_data.xml',
        'data/res_config_settings.xml',
        'data/mail_template_data.xml',
        'data/res_config_settings.xml',
        # security
        'security/ir.model.access.csv',
        'security/res_groups.xml',
        # views
        'views/product_template_view.xml',
        'views/templates_view.xml',
        'views/product_attribute_views.xml',
        'views/rating_rating_views.xml',
        'views/menu_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}