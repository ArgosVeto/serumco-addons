# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ConsultationType(models.Model):
    _name = 'consultation.type'
    _description = 'Consultation Type'

    name = fields.Char('Name', required=True)
    is_canvas = fields.Boolean('Is Canvas')
    chapters = fields.Text('Chapters')

    @api.model
    def _get_consultation_type(self, consultation=False):
        return self.search([('name', '=', consultation)], limit=1)