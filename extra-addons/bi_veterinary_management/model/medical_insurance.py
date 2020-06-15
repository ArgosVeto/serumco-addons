# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class medical_insurance(models.Model):
    _name = 'medical.insurance'
    _rec_name = 'insurance_company_id'
    
    number = fields.Char('Number')
    partner_id = fields.Many2one('res.partner', 'Owner')
    type =  fields.Selection([('state','State'),('private','Private'),('labour_union','Labour Union/ Syndical')],'Insurance Type')
    member_since= fields.Date('Member Since')
    insurance_company_id = fields.Many2one('res.partner', 'Insurance Compnay')
    category = fields.Char('Category')
    notes= fields.Text('Extra Info')
    member_exp = fields.Date('Expiration Date')
    plan_id = fields.Many2one('medical.insurance.plan','Plan')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: