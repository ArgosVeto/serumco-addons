# -*- coding: utf-8 -*-

from odoo import fields, models


class DocumentsTag(models.Model):
    _inherit = 'documents.tag'

    type = fields.Selection([('undefined', 'Undefined'), ('hypothese', 'Hypothese'), ('diagnostic', 'Diagnostic')],
                            'Type', default='undefined')
