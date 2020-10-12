# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class DocumentsTag(models.Model):
    _inherit = 'documents.tag'

    type = fields.Selection([('undefined', 'Undefined'), ('hypothese', 'Hypothese'), ('diagnostic', 'Diagnostic')],
                            'Type', default='undefined')
