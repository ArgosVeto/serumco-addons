# -*- coding: utf-8 -*-

import csv
import io
import base64
from odoo import models, fields, api, _
from datetime import time
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('approved', 'Approved'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ])
    is_centravet_order = fields.Boolean('Is Centravet Purchase Order', related='partner_id.is_centravet')
    operating_unit_request_line_ids = fields.Many2many('purchase.request.line', 'order_requested_line_rel', 'purchase_order',
                                                       'requested_line_id', 'Operating Unit Requested Lines')
    operating_unit_picking_ids = fields.Many2many('stock.picking', 'purchase_operating_unit_picking_rel', 'order_id', 'picking_id',
                                                  'Operating Units Internal Pickings', copy=False)
    operating_unit_picking_count = fields.Integer('Operating Units Pickings Count', compute='_compute_operating_unit_picking_count')

    def button_confirm(self):
        context = self._context.copy()
        if self._context.get('check_shipping_fees', False):
            carrier_id = self.partner_id.property_delivery_carrier_id
            if carrier_id and carrier_id.free_over and self.amount_untaxed < carrier_id.amount:
                context.update(active_id=self.id)
                return {
                    'name': _('Confirmation'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'purchase.confirmation.wizard',
                    'views': [(False, 'form')],
                    'target': 'new',
                    'context': context,
                }
            else:
                context.update(check_shipping_fees=False)
        emergency_orders, orders = self.split_centravet_emergency_order()
        res = super(PurchaseOrder, emergency_orders + orders).button_confirm()
        if emergency_orders and orders:
            return {
                'name': _('Orders confirmed'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'purchase.order',
                'domain': ['|', ('id', 'in', emergency_orders.ids), ('id', 'in', orders.ids)],
                'target': 'current',
                'context': context,
            }
        return res

    def split_centravet_emergency_order(self):
        emergency_orders = self.env['purchase.order']
        orders = self.env['purchase.order']
        for rec in self:
            if rec.is_centravet_order:
                if all(line.emergency for line in rec.order_line):
                    emergency_orders |= rec
                elif all(not line.emergency for line in rec.order_line):
                    orders |= rec
                else:
                    emergency_order = rec.copy()
                    emergency_order.order_line = [(2, line.id) for line in
                                                  emergency_order.order_line.filtered(lambda line: not line.emergency)]
                    rec.order_line = [(2, line.id) for line in rec.order_line.filtered(lambda line: line.emergency)]
                    emergency_orders |= emergency_order
                    orders |= rec
            else:
                emergency_orders |= rec
        return emergency_orders, orders

    def button_release(self):
        for rec in self:
            rec.send_order_mail()
            if rec.is_centravet_order and rec.is_centravet_planned_tour():
                rec.apply_discount(1)
        return super(PurchaseOrder, self).button_release()

    def button_approve(self, force=False):
        pending_orders = self.filtered(lambda order: order.is_centravet_order and all(not line.emergency for line in order.order_line))
        if pending_orders:
            super(PurchaseOrder, pending_orders).button_approve(force)
        return super(PurchaseOrder, self - pending_orders).button_release()

    def _create_picking(self):
        res = super(PurchaseOrder, self)._create_picking()
        for rec in self:
            if rec.operating_unit_request_line_ids:
                rec.create_operating_unit_picking()
        return res

    @api.depends('operating_unit_picking_ids')
    def _compute_operating_unit_picking_count(self):
        for rec in self:
            if rec.operating_unit_picking_ids:
                rec.operating_unit_picking_count = len(rec.operating_unit_picking_ids)
            else:
                rec.operating_unit_picking_count = 0

    def action_view_operating_pickings(self):
        self.ensure_one()
        return {
            'name': _('Operating units internal pickings'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('id', 'in', self.operating_unit_picking_ids.ids)],
            'target': 'current',
        }

    def send_order_mail(self):
        try:
            email_template = self.sudo().env.ref('argos_purchase.purchase_order_edi_mail_template_data')
            email_values = {}
            mail_attachments = self.generate_purchase_mail_attachment(self.is_centravet_order)
            email_values.update({'attachment_ids': [(6, 0, mail_attachments.ids)]})
            email_template.sudo().send_mail(self.id, force_send=True, email_values=email_values, raise_exception=True)
        except Exception as e:
            _logger.error(repr(e))

    @api.model
    def get_centravet_subscriber_code(self):
        return self.env['ir.config_parameter'].sudo().get_param('centravet.subscriber_code')

    def generate_purchase_mail_attachment(self, centravet=False):
        if centravet:
            file_data = base64.b64encode(self.generate_purchase_edi_file().getvalue().encode('utf-8'))
            sequence = self.env['ir.sequence'].next_by_code('centravet.purchase.order.seq')
            file_name = self.get_centravet_subscriber_code() + 'C' + sequence + '.csv'
        else:
            file_data = base64.b64encode(self.generate_purchase_report_file())
            file_name = self.name + '.pdf'
        return self.env['ir.attachment'].create({
            'name': file_name,
            'datas': file_data,
            'datas_fname': file_name,
        })

    def generate_purchase_report_file(self):
        report = self.env.ref('purchase.action_report_purchase_order')
        result, format = report.render_qweb_pdf([self.id])
        return result

    def generate_purchase_edi_file(self):
        subscriber_code = self.get_centravet_subscriber_code()
        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data, delimiter=',')
        for line in self.order_line:
            csv_writer.writerow([
                self.name,
                subscriber_code,
                self.operating_unit_id.email or '',
                self.operating_unit_id.password or '',
                self.operating_unit_id.code or '',
                line.product_id.cip or '',
                line.product_qty or 0,
                line.name or '',
                'PYXIS',
                '',
                '',
                '',
                fields.Date.from_string(line.date_planned).strftime('%Y%m%d') or '',
                ''
            ])
        return csv_data

    def is_centravet_planned_tour(self):
        self.ensure_one()
        calendar_id = self.partner_id.supplier_calendar_id
        now = fields.Datetime.now()
        now_time = now.time()
        if calendar_id:
            for attendance in calendar_id.attendance_ids:
                if int(attendance.dayofweek) - now.weekday() == 2 and time(16, 30) <= now_time <= time(20, 0):
                    return True
        return False

    def apply_discount(self, discount=False):
        if not discount:
            return
        for rec in self:
            rec.order_line.write({'discount': discount})
        return True

    def create_operating_unit_picking(self):
        self.ensure_one()
        operating_unit_request_lines = self.get_request_line_by_operating_unit()
        picking_obj = self.env['stock.picking']
        stock_move_obj = self.env['stock.move']
        for operating_unit, request_lines in operating_unit_request_lines.items():
            picking_vals = self._prepare_operating_unit_picking(operating_unit)
            picking = picking_obj.create(picking_vals)
            moves_vals = self._prepare_operating_unit_stock_moves(picking, request_lines)
            stock_move_obj.create(moves_vals)
            self.operating_unit_picking_ids = [(4, picking.id)]
        return True

    def get_request_line_by_operating_unit(self):
        result = {}
        operating_units = self.operating_unit_request_line_ids.mapped('operating_unit_id')
        for operating_unit in operating_units:
            if operating_unit in self.order_line.mapped('request_line_ids').mapped('operating_unit_id'):
                result[operating_unit] = self.operating_unit_request_line_ids.filtered(
                    lambda line: line.operating_unit_id == operating_unit)
        return result

    @api.model
    def _get_internal_picking_type(self, company_id):
        picking_type = self.env['stock.picking.type'].search([('code', '=', 'internal'), ('warehouse_id.company_id', '=', company_id)])
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search([('code', '=', 'internal'), ('warehouse_id', '=', False)])
        return picking_type[:1]

    @api.model
    def _prepare_operating_unit_picking(self, operating_unit):
        internal_picking_type = self._get_internal_picking_type(self.company_id.id)
        operating_unit_warehouse = self.env['stock.warehouse'].search([('operating_unit_id', '=', operating_unit.id)], limit=1)
        return {
            'picking_type_id': internal_picking_type.id,
            'partner_id': operating_unit.partner_id.id,
            'date': self.date_order,
            'location_dest_id': operating_unit_warehouse.lot_stock_id.id,
            'location_id': self._get_destination_location(),
            'company_id': self.company_id.id,
        }

    @api.model
    def _prepare_operating_unit_stock_moves(self, picking, request_lines):
        values = []
        request_lines = request_lines.filtered(lambda line: line in self.order_line.mapped('request_line_ids'))
        for request_line in request_lines:
            order_line_domain = [
                ('order_id', '=', self.id),
                ('product_id', '=', request_line.product_id.id or False),
                ('product_uom', '=', request_line.product_uom_id.id),
                ('account_analytic_id', '=', request_line.analytic_account_id.id or False),
            ]
            value = {
                'name': self.name or '',
                'product_id': request_line.product_id.id,
                'product_uom': request_line.product_uom_id.id,
                'product_uom_qty': request_line.product_uom_id._compute_quantity(request_line.product_qty, request_line.product_uom_id),
                'date': self.date_order,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
                'picking_id': picking.id,
                'partner_id': picking.partner_id.id,
                'state': 'draft',
                'company_id': self.company_id.id,
                'picking_type_id': picking.picking_type_id.id,
                'warehouse_id': picking.picking_type_id.warehouse_id.id,
            }
            for move_dict in values:
                move_difference = list(set(move_dict) - set(value))
                if move_difference == ['product_uom_qty'] or not move_difference:
                    move_dict['product_uom_qty'] += value['product_uom_qty']
                    value = False
            if value:
                order_lines = self.env['purchase.order.line'].search(order_line_domain)
                if order_lines:
                    value.update({'move_orig_ids': [(4, move.id) for move in order_lines.mapped('move_ids')]})
                values.append(value)
        return values
