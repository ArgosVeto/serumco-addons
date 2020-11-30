# -*- coding: utf-8 -*-

import logging
from odoo import models, api, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _order_fields(self, ui_order):
        result = super(PosOrder, self)._order_fields(ui_order)
        if 'sale_order_id' in result:
            quotation_obj = self.env['sale.order'].sudo().browse(result['sale_order_id'])
            if quotation_obj:
                # we set here to False, we set it to True after invoicing
                quotation_obj.pos_sold = False
        return result

    def check_qty_to_invoice(self, order):
        pos_order = self.search([('id', '=', order.id)])
        for line in pos_order.lines.filtered(
                lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.qty,
                                                                                          precision_rounding=l.product_id.uom_id.rounding)):
            if pos_order.sale_order_id:
                product_line = pos_order.sale_order_id.order_line.filtered(lambda l: l.product_id.id == line.product_id.id)
                # if the product from pos exist in consultation and do check
                if product_line.ids:
                    qty_invoiced_pos = sum(
                        pos_order.lines.filtered(lambda l: l.product_id.id == product_line[0].product_id.id).mapped(
                            'qty'))
                    if qty_invoiced_pos < product_line[0].qty_delivered:
                        raise UserError(_(
                            "The product %s could not be invoiced less than delivered. Please fix the real quantity") %
                                        product_line[0].name)

    @api.model
    def _process_order(self, order, draft, existing_order):
        if "to_invoice" in order and "data" in order:
            order["data"]["to_invoice"] = order["to_invoice"]
        pos_order_id = super(PosOrder, self)._process_order(order, draft, existing_order)
        return pos_order_id

    def _process_payment_lines(self, pos_order, order, pos_session, draft):
        super(PosOrder, self)._process_payment_lines(pos_order, order, pos_session, draft)
        self.check_qty_to_invoice(order)

    def create_picking(self):
        """Create a picking for each order and validate it."""
        Picking = self.env['stock.picking']
        # If no email is set on the user, the picking creation and validation will fail be cause of
        # the 'Unable to log message, please configure the sender's email address.' error.
        # We disable the tracking in this case.
        if not self.env.user.partner_id.email:
            Picking = Picking.with_context(tracking_disable=True)
        Move = self.env['stock.move']
        StockWarehouse = self.env['stock.warehouse']
        for order in self:
            if not order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu']):
                continue
            address = order.partner_id.address_get(['delivery']) or {}
            picking_type = order.picking_type_id
            return_pick_type = order.picking_type_id.return_picking_type_id or order.picking_type_id
            order_picking = Picking
            return_picking = Picking
            moves = Move
            location_id = picking_type.default_location_src_id.id
            consultation_of_service = all([x.product_id.type == 'service' for x in order.sale_order_id.order_line])
            if order.partner_id:
                destination_id = order.partner_id.property_stock_customer.id
            else:
                if (not picking_type) or (not picking_type.default_location_dest_id):
                    customerloc, supplierloc = StockWarehouse._get_partner_locations()
                    destination_id = customerloc.id
                else:
                    destination_id = picking_type.default_location_dest_id.id

            if picking_type:
                message = _("This transfer has been created from the point of sale session: "
                            "<a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (order.id, order.name)
                picking_vals = {
                    'origin': '%s - %s' % (order.session_id.name, order.name),
                    'partner_id': address.get('delivery', False),
                    'user_id': False,
                    'date_done': order.date_order,
                    'picking_type_id': picking_type.id,
                    'company_id': order.company_id.id,
                    'move_type': 'direct',
                    'note': order.note or "",
                    'location_id': location_id,
                    'location_dest_id': destination_id,
                }

                pos_qty = any([x.qty > 0 for x in order.lines if x.product_id.type in ['product', 'consu']])

                # only for non consultation or consultation of service only
                if (pos_qty and not order.sale_order_id.is_consultation) or (pos_qty and consultation_of_service):
                    order_picking = Picking.create(picking_vals.copy())
                    if self.env.user.partner_id.email:
                        order_picking.message_post(body=message)
                    else:
                        order_picking.sudo().message_post(body=message)

                neg_qty = any([x.qty < 0 for x in order.lines if x.product_id.type in ['product', 'consu']])

                # only for non consultation or consultation of service only
                if (neg_qty and not order.sale_order_id.is_consultation) or (neg_qty and consultation_of_service):
                    return_vals = picking_vals.copy()
                    return_vals.update({
                        'location_id': destination_id,
                        'location_dest_id': return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
                        'picking_type_id': return_pick_type.id
                    })
                    return_picking = Picking.create(return_vals)
                    if self.env.user.partner_id.email:
                        return_picking.message_post(body=message)
                    else:
                        return_picking.sudo().message_post(body=message)

            # managing picking moves for consultation previously loaded on pos
            consultation_picking_left = order.sale_order_id.picking_ids.filtered(lambda l: l.state == 'assigned')
            for line in order.lines.filtered(
                    lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.qty,
                                                                                              precision_rounding=l.product_id.uom_id.rounding)):
                # only for consultation and negative quantity from pos will be ignored
                if order.sale_order_id.is_consultation and line.qty > 0:
                    product_line = order.sale_order_id.order_line.filtered(
                        lambda l: l.product_id.id == line.product_id.id)
                    if len(product_line.ids) > 1:
                        raise UserError(_(
                            "These are more than one line of the same product in the consultation of %s") % order.sale_order_id.name)

                    # make sum to have the real quantity to deliver
                    # if the product from pos exist in consultation
                    if product_line.ids:
                        qty_invoiced_pos = sum(
                            order.lines.filtered(lambda l: l.product_id.id == product_line[0].product_id.id).mapped(
                                'qty'))
                        if product_line[0].qty_invoiced == 0 and  product_line[0].qty_delivered > 0:
                            qty = qty_invoiced_pos - product_line[0].qty_delivered
                        else:
                            qty = qty_invoiced_pos
                    else:
                        final_qty = sum(
                            order.lines.filtered(lambda l: l.product_id.id == line.product_id.id).mapped('qty'))
                        qty = final_qty

                    # if one left transfert to be treated
                    if len(consultation_picking_left) == 1:
                        for move in consultation_picking_left[0].move_ids_without_package:
                            if line.product_id.id == move.product_id.id:
                                # update qty on existing picking move with assigned state
                                move.quantity_done = qty

                        # if production is not on consultation thne add to the existing left picking
                        if not any([x.product_id.id == line.product_id.id for x in
                                    consultation_picking_left[0].move_ids_without_package]):
                            Move.create({
                                'name': line.name,
                                'product_uom': line.product_id.uom_id.id,
                                'picking_id': consultation_picking_left[0].id,
                                'picking_type_id': picking_type.id if line.qty >= 0 else return_pick_type.id,
                                'product_id': line.product_id.id,
                                'product_uom_qty': qty,
                                'quantity_done': qty,
                                'state': 'draft',
                                'location_id': location_id if line.qty >= 0 else destination_id,
                                'location_dest_id': destination_id if line.qty >= 0 else return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
                            })

                # in case we have consultation with only service line and we stockable product on pos create delivery, create picking link it to pos

                if consultation_of_service or not order.sale_order_id.is_consultation:
                    qty = abs(line.qty)
                    picking_id = order_picking.id if line.qty >= 0 else return_picking.id

                    moves |= Move.create({
                        'name': line.name,
                        'product_uom': line.product_id.uom_id.id,
                        'picking_id': picking_id,
                        'picking_type_id': picking_type.id if line.qty >= 0 else return_pick_type.id,
                        'product_id': line.product_id.id,
                        'product_uom_qty': qty,
                        'state': 'draft',
                        'location_id': location_id if line.qty >= 0 else destination_id,
                        'location_dest_id': destination_id if line.qty >= 0 else return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
                    })

            # prefer associating the regular order picking, not the return
            # this for non consultation
            if consultation_of_service or not order.sale_order_id.is_consultation:
                order.write({'picking_id': order_picking.id or return_picking.id})
                if return_picking:
                    order._force_picking_done(return_picking)
                if order_picking:
                    order._force_picking_done(order_picking)

                # when the pos.config has no picking_type_id set only the moves will be created
                if moves and not return_picking and not order_picking:
                    moves._action_assign()
                    moves.filtered(lambda m: m.product_id.tracking == 'none')._action_done()
            else:
                if consultation_picking_left:
                    order.write({'picking_id': consultation_picking_left[0].id})
                    consultation_picking_left.action_assign()

                    if consultation_picking_left._check_backorder():
                        wiz = self.env['stock.backorder.confirmation'].create(
                            {'pick_ids': [(4, p.id) for p in consultation_picking_left]})
                        wiz.process()
                    consultation_picking_left.action_done()

        return True

    def set_consultation_done(self):
        for order in self:
            order_line = order.sale_order_id.order_line
            # check if consultation must be set to pos sold
            qty_ordered = sum(order_line.mapped('product_uom_qty')) or 0.0
            qty_delivered = sum(order_line.mapped('qty_delivered')) or 0.0
            service_qty_ordered = sum(order_line.filtered(lambda l: l.product_id.type == 'service').mapped('product_uom_qty')) or 0.0
            service_qty_delivered = sum(order_line.filtered(lambda l: l.product_id.type == 'service').mapped('qty_delivered')) or 0.0

            # quantity delivered may be greater or equal than ordered
            if len(order.sale_order_id.picking_ids.filtered(lambda l: l.state == 'assigned')) == 0 \
                    and qty_delivered >= qty_ordered \
                    and service_qty_delivered >= service_qty_ordered:
                order.sale_order_id.pos_sold = True

            if order.sale_order_id.argos_state != 'consultation_done':
                order.sale_order_id.button_end_consultation()

    def action_pos_order_invoice(self):
        result = super(PosOrder, self).action_pos_order_invoice()

        # update service line quantity to be delivered manually on consultation according to quantity invoiced
        for order in self:
            if order.sale_order_id.is_consultation and order.state == 'invoiced' and order.account_move:
                service_list = order.sale_order_id.order_line.filtered(lambda l: l.product_id.type == 'service')
                if service_list:
                    for service_line in service_list:
                        if service_line.product_id.id in order.account_move.invoice_line_ids.mapped('product_id').ids:
                            quantity_invoiced = sum(order.account_move.invoice_line_ids.filtered(
                                lambda l: l.product_id.id == service_line.product_id.id).mapped(
                                'quantity'))
                            service_line.qty_delivered = quantity_invoiced + service_line.qty_delivered
                order.set_consultation_done()

                # update order_line and invoice for qty_invoiced on consultation
                invoice_line_ids = order.account_move.invoice_line_ids
                for consultation_line in order.sale_order_id.order_line:
                    if consultation_line.product_id.id in invoice_line_ids.mapped('product_id').ids:
                        for invoice_line in invoice_line_ids.filtered(lambda l: l.product_id.id == consultation_line.product_id.id):
                             consultation_line.invoice_lines = [(4, invoice_line.id)]

        return result
