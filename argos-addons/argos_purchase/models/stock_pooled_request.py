# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPooledRequest(models.TransientModel):
    _name = 'stock.pooled.request'

    @api.model
    def default_company(self):
        return self.env["res.company"].browse(self.env.company.id)

    requesting_operating_unit_id = fields.Many2one('operating.unit', 'Requesting Operating Unit', required=True)
    dest_location_id = fields.Many2one('stock.location', 'Destination Location', compute='compute_dest_location')
    line_ids = fields.One2many('stock.pooled.request.line', 'stock_pooled_request_id', 'Stock pooled request lines')
    company_id = fields.Many2one('res.company', default=default_company)

    @api.model
    def default_get(self, fields):
        self.check_pooled_picking_rules()
        request_obj = self.env['purchase.request']
        request_line_obj = self.env['purchase.request.line']
        res = super(StockPooledRequest, self).default_get(fields)
        request_lines = False
        if self._context.get('active_model') == 'purchase.request' and self._context.get('active_id', False):
            request_lines = request_obj.browse(self._context.get('active_id')).mapped('line_ids')
        elif self._context.get('active_model') == 'purchase.request.line' and self._context.get('active_ids', False):
            request_lines = request_line_obj.browse(self._context.get('active_ids'))
        if request_lines:
            products = request_lines.mapped('product_id')
            requesting_operatin_unit = request_lines.mapped('operating_unit_id')[0]
            res['requesting_operating_unit_id'] = requesting_operatin_unit.id
            res['line_ids'] = list(map(lambda line: (0, 0, line), self.get_lines(products)))
        return res

    def compute_dest_location(self):
        for rec in self:
            if rec.requesting_operating_unit_id:
                warehouse = self.env['stock.warehouse'].search([('operating_unit_id', '=', rec.requesting_operating_unit_id.id)], limit=1)
                if warehouse:
                    rec.dest_location_id = warehouse.lot_stock_id.id
                else:
                    rec.dest_location_id = False

    def check_pooled_picking_rules(self):
        request_obj = self.env['purchase.request']
        request_line_obj = self.env['purchase.request.line']
        request_lines = False
        if self._context.get('active_model') == 'purchase.request' and self._context.get('active_id', False):
            request_lines = request_obj.browse(self._context.get('active_id')).mapped('line_ids')
        elif self._context.get('active_model') == 'purchase.request.line' and self._context.get('active_ids', False):
            request_lines = request_line_obj.browse(self._context.get('active_ids'))
        if request_lines and any(not product.pooled_stock for product in request_lines.mapped('product_id')):
            raise UserError(_('Some request lines products is not configured for pooled stock picking.'))
        if request_lines and request_lines.filtered(lambda line: not line.operating_unit_id):
            raise UserError(_('Some request lines has no operating unit.'))
        if request_lines and len(request_lines.mapped('operating_unit_id')) > 1:
            raise UserError(_('You can create a pooled request only for one operating unit at time.'))

    @api.model
    def get_operating_units_stock_location(self):
        operating_units = self.env.user.operating_unit_ids.filtered(lambda ou: ou != self.requesting_operating_unit_id)
        warehouses = self.env['stock.warehouse'].search([('operating_unit_id', 'in', operating_units.ids)])
        return [(warehouse.operating_unit_id, warehouse.lot_stock_id) for warehouse in warehouses]

    @api.model
    def get_lines(self, products):
        self.check_pooled_picking_rules()
        ou_stock_locations = self.get_operating_units_stock_location()
        quant_obj = self.env['stock.quant']
        result = []
        for product in products:
            for ou, location in ou_stock_locations:
                quantity_available = quant_obj._get_available_quantity(product, location)
                if quantity_available:
                    result.append({
                        'source_operating_unit_id': ou.id,
                        'source_location_id': location.id,
                        'product_id': product.id,
                        'quantity_available': quantity_available,
                    })
        return result

    @api.model
    def _get_internal_picking_type(self, company_id):
        picking_type = self.env['stock.picking.type'].search([('code', '=', 'internal'), ('warehouse_id.company_id', '=', company_id)])
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search([('code', '=', 'internal'), ('warehouse_id', '=', False)])
        return picking_type[:1]

    @api.model
    def _prepare_internal_picking_values(self):
        internal_picking_type = self._get_internal_picking_type(self.company_id.id)
        picking_list = []
        locations_tuple = self.get_locations_tuple()
        for source, dest in locations_tuple:
            picking_vals = {
                'picking_type_id':  internal_picking_type.id,
                'partner_id': self.requesting_operating_unit_id.partner_id.id,
                'date': fields.Date.today(),
                'location_dest_id': dest.id,
                'location_id': source.id,
                'company_id': self.company_id.id,
                'move_lines': []
            }
            for line in self.line_ids.filtered(lambda l: l.source_location_id == source and l.dest_location_id == dest):
                if line.requested_quantity:
                    move_vals = {
                        'name': _('Pooled stock request'),
                        'product_id': line.product_id.id,
                        'product_uom': line.product_id.uom_id.id,
                        'product_uom_qty': line.uom_id._compute_quantity(line.requested_quantity, line.uom_id),
                        'date': fields.Date.today(),
                        'location_id': source.id,
                        'location_dest_id': dest.id,
                        'partner_id': self.requesting_operating_unit_id.partner_id.id,
                        'state': 'draft',
                        'company_id': self.company_id.id,
                        'picking_type_id': internal_picking_type.id,
                        'warehouse_id': internal_picking_type.warehouse_id.id,
                    }
                    picking_vals['move_lines'].append((0, 0, move_vals))
            if picking_vals['move_lines']:
                picking_list.append(picking_vals)
        return picking_list

    @api.model
    def get_locations_tuple(self):
        location_tuples = []
        for line in self.line_ids:
            location_tuples.append((line.source_location_id, line.dest_location_id))
        return list(set(location_tuples))

    def create_picking(self):
        picking_vals = self._prepare_internal_picking_values()
        if picking_vals:
            pickings = self.env['stock.picking'].create(picking_vals)
            return {
                'name': _('Internal pickings'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'stock.picking',
                'domain': [('id', 'in', pickings.ids)],
                'target': 'current',
            }


class StockPooledRequestLine(models.TransientModel):
    _name = 'stock.pooled.request.line'

    _order = 'source_operating_unit_id asc'

    stock_pooled_request_id = fields.Many2one('stock.pooled.request', 'Stock pooled request')
    source_operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', readonly=True)
    source_location_id = fields.Many2one('stock.location', 'Origin Location')
    dest_location_id = fields.Many2one('stock.location', 'Destination Location', related='stock_pooled_request_id.dest_location_id')
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    quantity_available = fields.Float('Quantity available', readonly=True)
    uom_id = fields.Many2one('uom.uom', 'Unit of measure', realated='product_id.uom_id')
    requested_quantity = fields.Float('Requested quantity', default=0.0)
