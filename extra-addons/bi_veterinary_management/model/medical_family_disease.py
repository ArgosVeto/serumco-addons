# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class medical_family_disease(models.Model):
    _name = 'medical.family.disease'
    
    medial_pathology_id = fields.Many2one('medical.pathology', 'Disease')
    relative = fields.Selection([('m','Mother'), ('f','Father'), ('b', 'Brother'), ('s', 'Sister'), ('a', 'aunt'), ('u', 'Uncle'), ('ne', 'Nephew'), ('ni', 'Niece'), ('gf', 'GrandFather'), ('gm', 'GrandMother')],string="Relative")
    maternal_paternal = fields.Selection([('m', 'Maternal'),('p', 'Paternal')],string="Maternal/Paternal")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: