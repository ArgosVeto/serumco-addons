# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class FieldsMapping(models.Model):
    _name = 'fields.mapping'
    _description = 'Fields Mapping'

    model_id = fields.Many2one('ir.model', string="Model")
    name = fields.Char(string="Source fields", required=True)
    destination = fields.Many2one('ir.model.fields', string="Destination fields", required=True)
    parser_id = fields.Many2one('xml.parser')
