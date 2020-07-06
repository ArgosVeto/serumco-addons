# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class ConsultationType(models.Model):
    _name = "consultation.type"
    _description = "Consultation Type"

    name = fields.Char('Consultation Name', required=True)

    @api.model
    def _get_consultation_type(self, consultation=False):
        return self.search([('name', '=', consultation)], limit=1)