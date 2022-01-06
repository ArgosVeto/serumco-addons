# -*- coding: utf-8 -*-
# Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details

from odoo import api, fields, models, _

class ResUsers(models.Model):
    _inherit = 'res.users'

    def shortlisted_clinic_partner(self):
        partner_id = self.partner_id
        partner_list = []
        if partner_id.clinic_shortlisted_ids:
            for p in partner_id.clinic_shortlisted_ids:
                partner_list.append(p.favorite_clinic_id.id)
        return partner_list


class ResPartner(models.Model):
    _inherit = 'res.partner'

    clinic_shortlisted_ids = fields.One2many('clinic.favorite', 'rel_partner_id', string='Contact')

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        print(""" Debugging on staging (def create):""")
        print(vals)
        return res

    def write(self, vals):
        print(""" Debugging on staging (def write):""")
        print(vals)
        super(ResPartner, self).write(vals)