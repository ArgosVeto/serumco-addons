# -*- coding: utf-8 -*-
# Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details

from odoo import api, fields, models, _

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    operating_unit_id = fields.Many2one('operating.unit',string="Clinic")
    contact_questions_id = fields.Many2one('contact.questions',string="Contact Question")


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    all_clinic = fields.Boolean(string="All Clinic")
    fav_clinic = fields.Boolean(string="Fav Clinic")

    @api.model
    def create(self,vals):
    	res = super(SaleOrder,self).create(vals)
    	if res.partner_id and res.partner_id.clinic_shortlisted_ids:
            res.operating_unit_id = res.partner_id.clinic_shortlisted_ids[0].id
            res.fav_clinic = True
    	return res