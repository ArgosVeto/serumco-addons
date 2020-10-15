# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hospital_icon = fields.Binary(string='Hospital')
    hour_icon = fields.Binary(string='Hour')
    invoice_icon = fields.Binary(string='Invoice')
    medical_icon = fields.Binary(string='Medical')

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        values = {
            'hospital_icon': self.hospital_icon,
            'hour_icon': self.hour_icon,
            'invoice_icon': self.invoice_icon,
            'medical_icon': self.medical_icon
        }
        self.env['res.company'].sudo().search([]).write(values)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        company_id = self.env.user.company_id.id
        company = self.env['res.company'].sudo().browse([company_id])
        res.update(
            hospital_icon=company.hospital_icon,
            hour_icon=company.hour_icon,
            invoice_icon=company.invoice_icon,
            medical_icon=company.medical_icon)
        return res
