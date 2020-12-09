# -*- coding: utf-8 -*-

from odoo import fields, models, api


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.depends('res_id')
    def _record_ref(self):
        for rec in self:
            model_id = self.env['ir.model'].sudo().search([('model', '=', rec.model)], limit=1)
            if model_id.transient:
                rec.record_ref = False
            else:
                super(MailMessage, rec)._record_ref()