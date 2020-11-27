# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class WebsiteMessageWizard(models.TransientModel):

    _name="website.message.wizard"
    _description="Wizard for show message for user."

    message = fields.Text(string="Message")

    def update_latest_record(self):
        active_model = self.env[self._context.get('active_model')]
        active_id = self._context.get('active_id') or self._context.get('active_ids')[0]
        for current_record in self:
            is_active_record = active_model.search([('is_active','=',True)])
            is_active_record.write({'is_active':False})
            active_record = active_model.browse(active_id)
            active_record.write({'is_active':True})
        return True

    def cancel(self):
        active_model = self.env[self._context.get('active_model')]
        active_id = self._context.get('active_id') or self._context.get('active_ids')[0]
        active_record = active_model.browse(active_id)
        active_record.write({'is_active':False})