# -*- coding: utf-8 -*-

import csv
import io
from odoo import models, fields, api, _
from datetime import timedelta
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

    cutoff_id = fields.Many2one('account.cutoff', 'Accrued Expense', copy=False)
    cutoff_move_ids = fields.Many2many('account.move', 'purchase_order_cutoff_move_rel', 'purchase_id',
                                       'cutoff_move_id', 'Accrued Expense moves', copy=False)
    cutoff_move_count = fields.Integer('Accrued Expense moves count', compute='compute_cutoff_move_count')
    from_website = fields.Boolean('Purchase due to procurement from website sales')

    def button_confirm(self):
        context = self._context.copy()
        if self._context.get('check_shipping_fees', False):
            carrier_id = self.partner_id.property_delivery_carrier_id
            if carrier_id and carrier_id.free_over:
                order_amount = 0
                if self.is_centravet_order and self.order_line.filtered(lambda line: line.emergency):
                    order_amount = sum(self.order_line.filtered(lambda line: line.emergency).mapped('price_subtotal'))
                else:
                    order_amount = self.amount_untaxed
                if order_amount < carrier_id.amount:
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
        emergency_orders.order_line.write({'date_planned': fields.Datetime.to_string(fields.Datetime.now() + timedelta(days=1))})
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
        now = fields.Datetime.now()
        for rec in self:
            if rec.is_centravet_order:
                if all(line.emergency for line in rec.order_line):
                    emergency_orders |= rec
                elif all(not line.emergency for line in rec.order_line):
                    orders |= rec
                else:
                    emergency_order = rec.copy({'order_line': False})
                    emergency_orders_lines = self.env['purchase.order.line']
                    for line in rec.order_line:
                        order_line = line.copy()
                        order_line.write({'purchase_request_lines': [(6, 0, line.purchase_request_lines.ids)]})
                        emergency_orders_lines |= order_line
                    if emergency_orders_lines:
                        emergency_order.write({'order_line': [(6, 0, emergency_orders_lines.ids)]})
                    emergency_order.order_line = [(2, line.id) for line in
                                                  emergency_order.order_line.filtered(lambda line: not line.emergency)]
                    rec.order_line = [(2, line.id) for line in rec.order_line.filtered(lambda line: line.emergency)]
                    emergency_orders |= emergency_order
                    emergency_orders.mapped('order_line').write({'date_planned': now + timedelta(days=1)})
                    orders |= rec
            else:
                emergency_orders |= rec
        return emergency_orders, orders

    def button_release(self):
        for rec in self:
            rec.send_order()
        return super(PurchaseOrder, self).button_release()

    def button_approve(self, force=False):
        pending_orders = self.filtered(lambda order: order.is_centravet_order and all(not line.emergency for line in order.order_line))
        if pending_orders:
            super(PurchaseOrder, pending_orders).button_approve(force)
        return (self - pending_orders).button_release()

    def send_order(self):
        try:
            if not self.is_centravet_order:
                email_template = self.sudo().env.ref('purchase.email_template_edi_purchase_done')
                email_values = {}
                email_template.sudo().send_mail(self.id, force_send=True, email_values=email_values, raise_exception=True)
            else:
                if not self.from_website:
                    file_data = self.generate_purchase_edi_file()
                    sequence = self.env['ir.sequence'].next_by_code('centravet.purchase.order.seq')
                    operating_unit = self.operating_unit_id or self.env.user.default_operating_unit_id
                    server = self.env.ref('argos_purchase.server_ftp_argos_purchase_order_data', raise_if_not_found=False)
                    filename = '%s%sC%s.csv' % (server.filename, operating_unit.code, sequence)
                    _logger.info('>>>>>>>>>>> %s not MTO' % (self.name,))
                    server.store_data(filename, file_data)

                else:
                    _logger.info('>>>>>>>>>>> %s from website' % (self.name,))
        except Exception as e:
            _logger.error(repr(e))

    def generate_purchase_edi_file(self):
        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data, delimiter=',')
        for line in self.order_line:
            csv_writer.writerow([
                self.name,
                self.operating_unit_id.code,
                self.operating_unit_id.email or '',
                self.operating_unit_id.password or '',
                self.operating_unit_id.argos_code or '',
                line.product_id.cip or '',
                line.product_qty or 0,
                line.name[:60] or '',
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
        if calendar_id:
            for attendance in calendar_id.attendance_ids:
                if int(attendance.dayofweek) - now.weekday() == 2:
                    self.order_line.write({'date_planned': fields.Datetime.to_string(now + timedelta(days=2))})
                    return True
        return False

    @api.depends('cutoff_move_ids')
    def compute_cutoff_move_count(self):
        for rec in self:
            if rec.cutoff_move_ids:
                rec.cutoff_move_count = len(rec.cutoff_move_ids)
            else:
                rec.cutoff_move_count = 0

    def action_view_cutoff(self):
        return {
            'name': _('Cutoff'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree, form',
            'res_model': 'account.move',
            'domain': [('id', 'in', self.cutoff_move_ids.ids)],
            'views': [(False, 'tree'), (False, 'form')],
            'target': 'current',
        }

    def reverse_cutoff_move(self):
        for rec in self:
            if rec.cutoff_id and rec.cutoff_id.move_id:
                reverse = self.env['account.move.reversal'].create({'move_id': rec.cutoff_id.move_id.id})
                result = reverse.reverse_moves()
                reverse_moves = False
                if result.get('res_id', False):
                    reverse_moves = self.env['account.move'].browse(result.get('res_id'))
                elif result.get('domain', False):
                    reverse_moves = self.env['account.move'].search(result.get('domain'))
                if reverse_moves:
                    reverse_moves.action_post()
                    rec.cutoff_move_ids = [(4, move.id) for move in reverse_moves]
        return True

    @api.depends('order_line.invoice_lines.move_id', 'order_line.invoice_lines.move_id.state')
    def _compute_invoice(self):
        super(PurchaseOrder, self)._compute_invoice()
        for rec in self:
            if rec.cutoff_id and rec.cutoff_id.move_id:
                cutoff_reversed_entry = self.env['account.move'].search([('reversed_entry_id', '=', rec.cutoff_id.move_id.id)])
                if any(invoice.state == 'posted' for invoice in rec.invoice_ids.filtered(lambda inv: inv.type == 'in_invoice')) \
                        and not cutoff_reversed_entry:
                    rec.reverse_cutoff_move()

    @api.model
    def schedule_release_approved_purchase(self):
        purchases = self.env['purchase.order'].search([('state', '=', 'approved')])
        for purchase in purchases:
            if purchase.is_centravet_order and purchase.is_centravet_planned_tour():
                purchase.button_release()
        return purchases
