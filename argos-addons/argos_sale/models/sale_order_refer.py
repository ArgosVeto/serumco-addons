# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleOrderRefer(models.TransientModel):
    _name = 'sale.order.refer'
    _description = 'Sale Order Refer'

    operating_unit_id = fields.Many2one('operating.unit', 'Refer To Clinic', required=True)
    employee_id = fields.Many2one('hr.employee', 'Refer to veterinary', required=True)
    consultation_type_id = fields.Many2one('consultation.type', 'Reason For Referral Request', placeholder='Comments')
    comments = fields.Text('Comments')

    def get_refer_values(self, order):
        self.ensure_one()
        return {
            'refer_employee_id': order.employee_id.id,
            'referent_partner_id': self.env.user.partner_id.id,
            'is_referral': True,
            'origin_order_id': order.id,
            'employee_id': self.employee_id.id,
            'operating_unit_id': self.operating_unit_id.id,
            'company_id': self.operating_unit_id.company_id.id,
            'team_id': False,
            'observation': self.comments,
            'state': 'draft',
            'argos_state': 'in_progress',
            'order_line': False,
        }

    def button_validate_refer(self):
        self.ensure_one()
        consultation = self.env['sale.order'].browse(self._context.get('active_id'))
        vals_overriden = self.get_refer_values(consultation)
        new_consultation = consultation.copy(vals_overriden)
        action = self.env.ref('argos_sale.action_consultations').read()[0]
        action.update({
            'views': [(self.env.ref('argos_sale.consultation_view_order_form').id, 'form')],
            'res_id': new_consultation.id,
            'target': 'current',
        })
        return action
