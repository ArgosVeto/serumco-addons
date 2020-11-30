# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True)
    pooled_stock_operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit For Pooled Stock',
                                                     domain=lambda self: [('id', '!=', self.operating_unit_id.id)])
    pooled_stock_exists = fields.Boolean('Pooled Stock Exists', compute='_compute_pooled_stock_exist')
    operating_unit_picking_ids = fields.Many2many('stock.picking', 'purchase_operating_unit_picking_rel', 'order_id', 'picking_id',
                                                  'Operating Units Internal Pickings', copy=False)
    operating_unit_picking_count = fields.Integer('Internal pickings count', compute='_compute_operating_unit_picking_count')
    request_confirm = fields.Boolean('Request confirm', compute='_compute_request_confirm')

    @api.onchange('requested_by')
    def onchange_requested_by(self):
        self.operating_unit_id = self.requested_by.default_operating_unit_id

    @api.onchange('operating_unit_id')
    def onchange_operating_unit(self):
        type_obj = self.env["stock.picking.type"]
        types = type_obj.search(
            [("code", "=", "incoming"), ("warehouse_id.operating_unit_id", "=", self.operating_unit_id.id)]
        )
        if not types:
            types = type_obj.search(
                [("code", "=", "incoming"), ("warehouse_id.company_id", "=", self.env.company.id)]
            )
        self.picking_type_id = types[:1]

    @api.depends('line_ids')
    def _compute_pooled_stock_exist(self):
        for rec in self:
            if any(line.pooled_stock for line in rec.line_ids):
                rec.pooled_stock_exists = True
            else:
                rec.pooled_stock_exists = False

    @api.model
    def create(self, vals):
        res = super(PurchaseRequest, self).create(vals)
        res.button_to_approve()
        res.button_approved()
        return res

    @api.model
    def get_lines_available_quantity(self):
        self.ensure_one()
        available_lines = self.env['purchase.request.line']
        if not self.pooled_stock_exists or not self.pooled_stock_operating_unit_id:
            return available_lines
        pooled_location = self.get_operating_unit_stock_location(self.pooled_stock_operating_unit_id)
        if not pooled_location:
            return available_lines
        return self.line_ids.filtered(lambda line: line.pooled_stock)

    def get_lines_per_supplier(self):
        self.ensure_one()
        suppliers = self.line_ids.mapped('supplier_id')
        result = {}
        for supplier in suppliers:
            lines_to_purchase = self.line_ids.filtered(lambda line: line.supplier_id == supplier and not line.pooled_stock)
            if lines_to_purchase:
                result[supplier] = lines_to_purchase
        return result

    def create_orders(self):
        for rec in self:
            lines_per_supplier = rec.get_lines_per_supplier()
            for supplier in lines_per_supplier.keys():
                wiz = self.env['purchase.request.line.make.purchase.order'].with_context(active_ids=lines_per_supplier.get(
                    supplier).ids, active_model='purchase.request.line', operating_unit=self.operating_unit_id.id).create({'supplier_id':
                         supplier.id})
                wiz.make_purchase_order()
        return True

    @api.model
    def get_operating_unit_stock_location(self, operating_unit):
        warehouse = self.env['stock.warehouse'].search([('operating_unit_id', '=', operating_unit.id)], limit=1)
        return warehouse.lot_stock_id

    @api.model
    def get_locations_tuple(self):
        self.ensure_one()
        if self.pooled_stock_operating_unit_id and self.operating_unit_id:
            source_location = self.get_operating_unit_stock_location(self.pooled_stock_operating_unit_id)
            dest_location = self.get_operating_unit_stock_location(self.operating_unit_id)
            return source_location, dest_location
        return False, False

    @api.model
    def _get_internal_picking_type(self):
        picking_type = self.env['stock.picking.type'].search([('code', '=', 'internal'),
                                                              ('warehouse_id.company_id', '=', self.env.company.id),
                                                              ('warehouse_id.operating_unit_id', '=',
                                                               self.pooled_stock_operating_unit_id.id)])
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search([('code', '=', 'internal'), ('warehouse_id', '=', False)])
        return picking_type[:1]

    @api.model
    def _prepare_internal_picking_values(self):
        self.ensure_one()
        internal_picking_type = self._get_internal_picking_type()
        picking_list = []
        source_location, dest_location = self.get_locations_tuple()
        if source_location and dest_location:
            picking_vals = {
                'picking_type_id': internal_picking_type.id,
                'date': fields.Date.today(),
                'location_dest_id': dest_location.id,
                'location_id': source_location.id,
                'company_id': self.company_id.id,
                'move_lines': []
            }
            for line in self.get_lines_available_quantity():
                if line.product_qty:
                    move_vals = {
                        'name': _('Pooled stock request'),
                        'product_id': line.product_id.id,
                        'product_uom': line.product_id.uom_id.id,
                        'product_uom_qty': line.product_uom_id._compute_quantity(line.product_qty, line.product_uom_id),
                        'date': fields.Date.today(),
                        'location_id': source_location.id,
                        'location_dest_id': dest_location.id,
                        'state': 'draft',
                        'company_id': self.company_id.id,
                        'picking_type_id': internal_picking_type.id,
                        'warehouse_id': internal_picking_type.warehouse_id.id,
                    }
                    picking_vals['move_lines'].append((0, 0, move_vals))
            if picking_vals['move_lines']:
                picking_list.append(picking_vals)
        return picking_list

    def create_internal_picking(self):
        picking_obj = self.env['stock.picking']
        for rec in self:
            picking_vals = rec._prepare_internal_picking_values()
            if picking_vals and rec.pooled_stock_exists:
                picking = picking_obj.create(picking_vals)
                rec.operating_unit_picking_ids = [(4, picking.id)]
        return True

    def _compute_operating_unit_picking_count(self):
        for rec in self:
            rec.operating_unit_picking_count = len(rec.operating_unit_picking_ids)

    def action_view_ou_internal_picking(self):
        self.ensure_one()
        return {
            'name': _('Operating units internal pickings'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('id', 'in', self.operating_unit_picking_ids.ids)],
            'target': 'current',
        }

    def button_confirm(self):
        for rec in self:
            rec.create_orders()
            for purchase in rec.mapped("line_ids.purchase_lines.order_id"):
                purchase.button_confirm()
            rec.create_internal_picking()
            for picking in rec.operating_unit_picking_ids:
                picking.action_assign()
        return True

    def _compute_request_confirm(self):
        for rec in self:
            if rec.mapped("line_ids.purchase_lines.order_id") or rec.operating_unit_picking_ids:
                rec.request_confirm = True
            else:
                rec.request_confirm = False
