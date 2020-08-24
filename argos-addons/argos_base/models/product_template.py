# -*- coding: utf-8 -*-

from odoo import models, fields, registry, http, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    gtin = fields.Char('GTIN Code')
    ean = fields.Char('EAN Code')
    cip = fields.Char('CIP Code')
