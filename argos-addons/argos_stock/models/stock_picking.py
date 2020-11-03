# -*- coding: utf-8 -*-

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_arg_prescription = fields.Boolean('Is prescription')
    return_reason = fields.Selection([
        ('no_order', 'Not ordered products'),
        ('damaged', 'Products damaged upon receipt'),
        ('improper_date', 'Non-compliant products - expiration date too short'),
        ('improper_conservation', 'Non-compliant products - storage conditions (cold, etc.) not respected'),
        ('improper_promotional', 'Non-compliant products - promotional conditions'),
        ('error', 'Order error'),
        ('batch_recall', 'Batch recall by laboratory')
    ], 'Return Reason')
    scrap_reason = fields.Selection([
        ('expiration_date', 'Expiration date passed'),
        ('use_date', 'Use date after first use passed'),
        ('storage_condition', 'Storage conditions not respected'),
        ('product_deteriorated', 'Products deteriorated in the clinic'),
        ('return_medicine', 'Customer return cannot be reintegrated to stock - medicine'),
        ('return_other', 'Customer return cannot be reintegrated to stock - other'),
        ('batch_recall', 'batch recall by laboratory - destruction on site')
    ], 'Scrap reason')
