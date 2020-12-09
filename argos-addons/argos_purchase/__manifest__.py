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
        'purchase_subscription',
        'purchase_requisition',
        'account_cutoff_accrual_picking',
        'delivery',
        'resource',
    ],
    'data': [
        #security
        'security/ir.model.access.csv',
        'security/purchase_request_rules.xml',
        #data
        'data/ir_sequence_data.xml',
        'data/purchase_order_edi_template.xml',
        'data/purchase_approved_cron.xml',
        'data/server_ftp_data.xml',
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
