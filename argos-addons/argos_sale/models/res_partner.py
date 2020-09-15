# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import ast


class ResPartner(models.Model):
    _inherit = 'res.partner'

    consultation_ids = fields.One2many('sale.order', 'patient_id', 'Consultations')

    def button_create_consultation(self):
        self.ensure_one()
        action = self.env.ref('argos_sale.action_consultations').read()[0]
        action['views'] = [(self.env.ref('argos_sale.consultation_view_order_form').id, 'form')]
        action['context'] = ast.literal_eval(action['context'])
        action['context'].update({
            'default_patient_id': self.id,
            'default_employee_id': self.employee_id.id,
            'default_is_consultation': True,
        })
        return action