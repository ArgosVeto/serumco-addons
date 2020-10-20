# -*- coding: utf-8 -*-
{
    'name': 'Argos Purchase',
    'summary': '',
    'category': 'Purchase',
    'version': '1.0',
    'sequence': -83,
    'author': 'ArkeUp',
    'license': 'AGPL-3',
    'website': 'https://arkeup.com',
    'description': '',
    'depends': [
        'argos_operating_unit',
        'argos_stock',
        'argos_account',
        'purchase_operating_unit',
        'purchase_request',
        'purchase_order_approved',
        'purchase_discount',
        'merge_purchase_order',
        'bi_convert_purchase_from_sales',
        'delivery',
        'resource',
    ],
    'data': [
        #security
        'security/ir.model.access.csv',
        #data
        'data/ir_sequence_data.xml',
        'data/purchase_order_edi_template.xml',
        #views
        'views/res_partner_views.xml',
        'views/product_template_views.xml',
        'views/purchase_order_views.xml',
        'views/purchase_confirmation_views.xml',
        'views/stock_move_line_views.xml',
        'views/purchase_request_views.xml',
        'views/menu_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
