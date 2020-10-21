# -*- coding: utf-8 -*-

{
    'name': 'Pos Load Sales Order',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'WebVeer',
    'summary': "Pos load sales order" ,
    'description': """
        Pos load sales order.
""",
    'depends': ['sale','point_of_sale'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        # 'views/sequence.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'images': [
        'static/description/list.jpg',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 100,
    'currency': 'EUR',
}
