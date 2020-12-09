# -*- coding: utf-8 -*-

from odoo import models, api, fields


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', related='request_id.operating_unit_id')
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type', related='request_id.picking_type_id')
    pooled_stock = fields.Boolean('Pooled stock')
    supplier_id = fields.Many2one(inverse='_write_supplier_id')
    emergency = fields.Boolean('Emergency')
    is_centravet = fields.Boolean('Is Supplier Centravet', related='supplier_id.is_centravet')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.pooled_stock = self.product_id.pooled_stock
        super(PurchaseRequestLine, self).onchange_product_id()

    def _write_supplier_id(self):
        for rec in self:
            if rec.supplier_id and rec.supplier_id not in rec.product_id.seller_ids.mapped('name'):
                rec.product_id.seller_ids = [(0, 0, {'name': rec.supplier_id.id})]

    @api.depends()
    def _compute_is_editable(self):
        for rec in self:
            if rec.request_id.state == 'done':
                rec.is_editable = False
            else:
                rec.is_editable = True
        for rec in self.filtered(lambda p: p.purchase_lines):
            rec.is_editable = False