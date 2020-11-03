# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def default_get(self, fields_list):
        res = super(MailMessage, self).default_get(fields_list)
        if 'website_published' in fields_list:
            res.update({'website_published': False})
        return res
