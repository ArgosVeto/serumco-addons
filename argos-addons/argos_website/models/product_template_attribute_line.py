# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplateAttributeLine(models.Model):
    _inherit = 'product.template.attribute.line'

    is_attribute_visible = fields.Boolean('Filter visible in web', related='attribute_id.is_attribute_visible')