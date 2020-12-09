# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order'

    @api.model
    def get_default_picking_type(self):
        return self.env['purchase.order']._get_picking_type(self.env.company.id)

    @api.model
    def _prepare_purchase_order(self, picking_type, group_id, company, origin):
        res = super(PurchaseRequestLineMakePurchaseOrder, self)._prepare_purchase_order(picking_type, group_id, company, origin)
        res['picking_type_id'] = self.get_default_picking_type().id
        return res

    @api.model
    def _check_multiple_operating_unit_request(self):
        if self._context.get('active_model', False) == 'purchase.request.line' and self._context.get('active_ids', False):
            request_lines = self.env['purchase.request.line'].browse(self._context.get('active_ids'))
            if len(request_lines.mapped('operating_unit_id')) >= 1:
                return True
        if self._context.get('active_model', False) == 'purchase.request' and self._context.get('active_ids', False):
            request_lines = self.env['purchase.request'].browse(self._context.get('active_ids')).mapped('line_ids')
            if len(request_lines.mapped('operating_unit_id')) >= 1:
                return True
        return False

    def make_purchase_order(self):
        res = super(PurchaseRequestLineMakePurchaseOrder, self).make_purchase_order()
        if self._check_multiple_operating_unit_request():
            purchases = self.env['purchase.order'].search(res['domain'])
            request_lines = self.item_ids.filtered(lambda item: item.line_id.operating_unit_id and item.line_id.product_id.type in [
                'product', 'consu'] and item.line_id.picking_type_id != self.get_default_picking_type().id)
            purchases.operating_unit_request_line_ids = [(6, 0, request_lines.mapped('line_id').ids)]
        return res

    @api.model
    def _check_valid_request_line(self, request_lines):
        request_line_obj = self.env["purchase.request.line"]
        if self._context.get('active_model', False) == 'purchase.request.line' and self._check_multiple_operating_unit_request():
            request_lines = request_line_obj.browse(request_lines)
            if request_lines.filtered(lambda line: line.request_id.state == 'done'):
                raise UserError(_("Purchase request has already been completed."))
            if request_lines.filtered(lambda line: line.purchase_state == 'done'):
                raise UserError(_("Purchase related to some request has already been completed."))
            if request_lines.filtered(lambda line: line.request_id.state != 'approved'):
                raise UserError(_("There are some not approved purchase request."))
        else:
            super(PurchaseRequestLineMakePurchaseOrder, self)._check_valid_request_line(request_lines)
