# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    task_ids = fields.One2many('project.task', 'order_id', 'Analysis',
                               domain=[('task_id', '=', False), ('task_type', '=', 'analysis')])
    imagery_task_ids = fields.One2many('project.task', 'order_id', 'Imagery',
                                       domain=[('task_id', '=', False), ('task_type', '=', 'imagery')])
