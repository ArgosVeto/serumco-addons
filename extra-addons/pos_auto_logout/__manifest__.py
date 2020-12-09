# -*- coding: utf-8 -*-

{
    'name': 'Pos Automatic Logout',
    'version': '1.0',
    'category': 'All',
    'sequence': 6,
    'author': 'ErpMstar Solutions',
    'summary': 'Allows you to automatically logout when you do not interact with Pos.',
    'depends': ['point_of_sale'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/view.xml',
        # 'views/templates.xml',
    ],
    'qweb': [
        # 'static/src/xml/pos.xml',
    ],
    'images': [
        'static/description/conifg.jpg',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 25,
    'currency': 'EUR',
    'bootstrap': True,
}
