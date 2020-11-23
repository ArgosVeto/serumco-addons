# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ConsultationType(models.Model):
    _name = 'consultation.type'
    _description = 'Consultation Type'

    name = fields.Char('Name', required=True)
    is_canvas = fields.Boolean('Is Canvas')
    is_default = fields.Boolean(string='Default', default=False)
    chapters = fields.Text('Chapters')

    @api.model
    def _get_consultation_type(self, consultation=False):
        return self.search([('name', '=', consultation)], limit=1)

    @api.model
    def create(self, vals):
        res = super(ConsultationType, self).create(vals)
        if res.is_default:
            res.update_default_type()
        return res

    def write(self, vals):
        res = super(ConsultationType, self).write(vals)
        if vals.get('is_default', False):
            for rec in self.filtered(lambda l: l.is_default):
                rec.update_default_type()
        return res

    def update_default_type(self):
        if self.is_default:
            self.search([('id', '!=', self.id), ('is_default', '=', True)]).write({'is_default': False})
