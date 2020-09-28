# -*- coding: utf-8 -*-
# Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details

from odoo import api, fields, models, _

class HrApplicant(models.Model):
    _inherit = 'hr.applicant'
    
    actual_post = fields.Char(string="Actual Post")
    code_postal = fields.Char(string="Code Postal")
    city = fields.Char(string="Ville")
    address =  fields.Char(string="Address")
    country_id = fields.Many2one('res.country',string="Country")
    number_of_exp = fields.Char(string="Number of experience")
    agglomeration_id = fields.Many2one('applicant.agglomeration',string="Agglomeration")
    job_type_id = fields.Many2one('job.type',string="Job Type")
    
class Agglomeration(models.Model):
    _name = "applicant.agglomeration"
    
    name = fields.Char(string="Agglomeration")
    

class JobTag(models.Model):
    _name = "job.tag"
    
    name = fields.Char(string="Job Tag")


class HrJob(models.Model):
    _inherit = 'hr.job'

    job_type_id = fields.Many2one('job.type',string="Job Type")
    job_tag_ids = fields.Many2many('job.tag',string="Job Tag")
    
    
    
    
from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    note = fields.Text(string="Note for Website")