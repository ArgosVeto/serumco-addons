# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class res_partner(models.Model):
    _inherit = "res.partner"
    
    is_patient = fields.Boolean('Patient')
    is_owner = fields.Boolean(string="Owner")
    is_person = fields.Boolean('Person')
    is_doctor = fields.Boolean('Doctor')
    is_institution = fields.Boolean('Institution')
    is_insurance_company =  fields.Boolean('Insurance Company')
    is_pharmacy =  fields.Boolean('Pharmacy') 
    insurance_ids = fields.One2many('medical.insurance','insurance_company_id','Insurance')
    ref = fields.Char('ID Number')
    relationship = fields.Char(string='Relationship')
    relative_id = fields.Many2one('res.partner',string="Relative_id")
    is_pet = fields.Boolean(string="Pet")
    owner_id = fields.Many2one('res.partner')
    insurance = fields.One2many('medical.insurance','partner_id')
    domiciliary_id = fields.Many2one('medical.domiciliary.unit')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: