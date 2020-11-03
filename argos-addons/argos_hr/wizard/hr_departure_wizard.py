# -*- coding: utf-8 -*-

from odoo import fields, models


class HrDepartureWizard(models.TransientModel):
    _inherit = 'hr.departure.wizard'

    leave_date = fields.Date('Leave Date', default=lambda self: fields.Date.today())

    def action_register_departure(self):
        res = super(HrDepartureWizard, self).action_register_departure()
        self.employee_id.leave_date = self.leave_date
        return res
