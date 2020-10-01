# -*- coding: utf-8 -*-
# Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details

from odoo import api, fields, models, _
# operating.unit.service

# class Services(models.Model):
#     _name = 'service.provide'
#object to delete
#     _description = 'Service Provide'

#     name = fields.Char(string="Service")
#     description = fields.Char(string="Description")
#     service_partner_id = fields.Many2one('res.partner',string="Partner")


class ClinicFavorite(models.Model):
    _name = 'clinic.favorite'
    _description = 'Clinic Favorite'
    _rec_name = 'favorite_clinic_id'
    
    favorite_clinic_id = fields.Many2one('operating.unit', string='Operating unit')
    rel_partner_id = fields.Many2one('res.partner', string='Operating unit')

# class ClinicType(models.Model):
#     _name = 'clinic.type'
#     _description = 'Clinic Type'

    # name = fields.Char(string="Name")
# 

class PracticalService(models.Model):
    _name = 'practical.service'
    _description = 'Practical Service'

    name = fields.Char(string="Name")

class ClinicImage(models.Model):
    _name = 'clinic.image'
    _description = 'clinic image'


    name = fields.Char("Name")
    image_1920 = fields.Image(required=True,string="Clinic Image")
    clinic_image_id = fields.Many2one('res.partner',string="Clinic")

class Contactquestions(models.Model):
    _name = 'contact.questions'
    _description = 'Contact questions'

    name = fields.Char(string="Contact")

class Agglomeration(models.Model):
    _name = "applicant.agglomeration"
    _description = 'Applicant Agglomeration'

    
    name = fields.Char(string="Agglomeration")

class JobType(models.Model):
    _name = "job.type"
    _description = 'job type'
    
    name = fields.Char(string="Job Type")   
