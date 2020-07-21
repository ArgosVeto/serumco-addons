# -*- coding: utf-8 -*-

from odoo import models, fields, registry, http, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    mother_class = fields.Char('Class')
    child_class = fields.Char('Sub Class')
    sub_child_class = fields.Char('Sub child class')
    gtin = fields.Char('GTIN Code')
    ean = fields.Char('EAN Code')
    cip = fields.Integer('CIP Code')
