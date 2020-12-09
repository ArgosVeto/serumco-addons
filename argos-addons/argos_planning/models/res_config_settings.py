# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    appointment_constraint = fields.Boolean(string='Appointment constraint')

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        values = {
            'appointment_constraint': self.appointment_constraint
        }
        self.env['res.company'].sudo().search([]).write(values)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        company_id = self.env.user.company_id.id
        company = self.env['res.company'].sudo().browse([company_id])
        res.update(appointment_constraint=company.appointment_constraint)
        return res
