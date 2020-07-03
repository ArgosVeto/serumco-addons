# -*- coding: utf-8 -*-

from odoo import models, fields, registry, http, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    mother_class = fields.Char(string="Class")
    child_class = fields.Char(string="Sub Class")
    sub_child_class = fields.Char(string="Sub child class")
    gtin = fields.Char(string="GTIN Code")
    ean = fields.Char(string="EAN Code")
    cip = fields.Integer(string="CIP Code")
