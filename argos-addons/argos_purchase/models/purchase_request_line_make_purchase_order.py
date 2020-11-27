# -*- coding: utf-8 -*-

from odoo import models, api, fields, _


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order'

    @api.model
    def get_default_picking_type(self):
        if self._context.get('operating_unit', False):
            operating_unit = self._context.get('operating_unit')
            default_warehouse = self.env['stock.warehouse'].search([('operating_unit_id', '=', operating_unit)], limit=1)
            if default_warehouse:
                default_picking_type = self.env['stock.picking.type'].search([('warehouse_id', '=', default_warehouse.id),
                                                                              ('code', '=', 'incoming'),
                                                                              ('warehouse_id.company_id', '=', self.env.company.id)],
                                                                             limit=1)
                return default_picking_type
        return self.env['purchase.order']._get_picking_type(self.env.company)

    @api.model
    def _prepare_item(self, line):
        vals = super(PurchaseRequestLineMakePurchaseOrder, self)._prepare_item(line)
        vals.update({'emergency': line.emergency})
        return vals

    @api.model
    def _prepare_purchase_order(self, picking_type, group_id, company, origin):
        res = super(PurchaseRequestLineMakePurchaseOrder, self)._prepare_purchase_order(picking_type, group_id, company, origin)
        if self._context.get('operating_unit', False):
            default_picking_type = self.get_default_picking_type()
            res['picking_type_id'] = default_picking_type.id
            res['operating_unit_id'] = self._context.get('operating_unit')
            res['requesting_operating_unit_id'] = self._context.get('operating_unit')
        return res

    @api.model
    def _prepare_purchase_order_line(self, po, item):
        vals = super(PurchaseRequestLineMakePurchaseOrder, self)._prepare_purchase_order_line(po, item)
        vals.update({'emergency': item.emergency})
        return vals


class PurchaseRequestLineMakePurchaseOrderItem(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order.item'

    emergency = fields.Boolean('Emergency')
