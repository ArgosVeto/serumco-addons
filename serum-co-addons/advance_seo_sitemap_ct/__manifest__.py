# -*- coding: utf-8 -*-
{   
    # App information
    'name': 'Advance SEO Sitemap',
    'version': '1.0',
    'summary': 'This app is used to generate advance SEO sitemap.',
    'category': 'Website',
    'license': 'OPL-1',
    'images': ['static/description/cover_image.jpg'],

     # Dependencies
    'depends': ['website_sale'],
    
    #views
    'data': [
        'views/product_template_view.xml',
        'views/product_public_category_view.xml',
        'views/website_page_view.xml'
    ],

     'qweb': [
    ],

    # Author
    'author': '',
    'website': '',
    'installable': True,
    'auto_install': False,
}
