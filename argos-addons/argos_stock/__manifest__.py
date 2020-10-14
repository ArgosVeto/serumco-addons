# -*- coding: utf-8 -*-
{
    'name': 'Argos Stock',
    'summary': '',
    'category': 'Stock',
    'version': '1.0',
    'sequence': -93,
    'author': 'ArkeUp',
    'license': 'AGPL-3',
    'website': 'https://arkeup.com',
    'description': '',
    'depends': [
        'sale_stock',
        'argos_product',
        'argos_sale',
    ],
    'data': [
        # security
        'security/ir.model.access.csv',
        # views
        'views/product_template_views.xml',
        'views/prescription_report.xml',
        'views/prescription_report_template.xml',
        'views/mail_data.xml',
        'views/stock_picking_print_views.xml',
        'views/sale_order_views.xml',
        'views/stock_picking_views.xml',
        'views/stock_menu_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
