# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name' : 'Products Rating',
    'version' : '13.0.1.1',
    'summary': 'Products Rating',
    'author': 'Bizople Solutions Pvt. Ltd.',
    'website': 'https://www.bizople.com',
    'sequence': 1,
    'description': """
        Products Rating
    """,
    'category': '',
    'images' : [],
    'depends' : ['website_sale','website_rating'],
    'data': [
        'views/template.xml',
        ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}