# -*- coding: utf-8 -*-

from odoo import models, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _get_contact_url(self, phone=False):
        if not phone:
            return ''
        phone = phone.replace(' ', '')
        callee_inter_format = '+' + phone
        callee_national_format = '0' + phone[2:]
        partner = self.search(['|', ('phone', 'in', [phone, callee_national_format, callee_inter_format]),
                               ('mobile', 'in', [phone, callee_inter_format, callee_national_format])], limit=1)
        if not partner:
            return _('This number %s has contacted you but does not have a contact sheet.') % phone
        config = self.env['ir.config_parameter'].sudo()
        url = config.get_param('web.base.url')
        url += '/web#'
        params = 'id=%s&action=%s&model=%s&view_type=%s' % \
                 (partner.id, self.env.ref('contacts.action_contacts', raise_if_not_found=False).id, 'res.partner',
                  'form')
        url += params
        return _('<a href="%s">%s</a> has contacted you') % (url, partner.name)
