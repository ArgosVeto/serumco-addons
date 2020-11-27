# -*- coding: utf-8 -*-
{
    'name': """
SEO-URL Redirect, Website Multiple URL Rewrite, Bulk URL redirect 
""",

    'summary': """
       Set any SEO URL for your odoo website, Bulk URL redirect this module is most preferable for Ecommerce Shop and other odoo website""",

    'description': """
       This module allows to set redirection or rewrite URL in odoo using Following Steps:
    """,
    'category': 'Website',
    'version': '13.0.0.0.0',

    'depends': ['base', 'website','product','website_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/product_inherit.xml',
        'data/seo_data.xml',
        'views/website_seo_redirection_view.xml',
    ],
    'demo': [
        'demo/demo.xml',
        'demo/assets_demo.xml',
        'demo/website_seo_redirection_demo.xml',
    ],
    'author': '',
    'installable': True,
    'license': 'AGPL-3',
    'external_dependencies': {'python': ['qrcode', 'pyotp']},
    'images': ['static/description/images/Banner-Img.png'],
}
