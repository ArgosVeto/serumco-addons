# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductApproval(models.Model):
    _name = 'product.approval'
    _description = 'Product Approval'

    name = fields.Char('Name', required=True)
    renewal = fields.Char('Renewal', translate=True)
