# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round, float_compare
from dateutil.relativedelta import relativedelta
from datetime import datetime


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    initial_qty = fields.Float('Initial Quantity', related='move_id.sale_line_id.product_uom_qty')
    delivered_qty = fields.Float('Delivered Quantity', related='move_id.sale_line_id.qty_delivered')
    remaining_qty = fields.Float('Remaining Quantity', compute='_compute_remaining_qty')
    prescription = fields.Char(related='picking_id.sale_id.name', string='Prescription n°')
    employee_id = fields.Many2one(related='picking_id.sale_id.employee_id', string='Delivered By')
    order_number = fields.Char(related='picking_id.sale_id.employee_id.order_number', string='Order n°')
    partner_id = fields.Many2one(related='move_id.partner_id', string='Customer/Address')
    chip = fields.Char(related='picking_id.sale_id.patient_id.chip_identification', string='Chip ID')
    tattoo = fields.Char(related='picking_id.sale_id.patient_id.tattoo_number', string='Tattoo n°')
    passport = fields.Many2one(related='picking_id.sale_id.patient_id.passport_id', string='Passport')
    peremption = fields.Datetime(related='lot_id.life_date', string='Expiration Date')
    peremption_1 = fields.Datetime(string='Expiration Date')

    @api.depends('initial_qty', 'delivered_qty', 'qty_done')
    def _compute_remaining_qty(self):
        for line in self:
            line.remaining_qty = line.initial_qty - (line.delivered_qty + line.qty_done)

    @api.onchange('lot_name')
    def _onchange_lot_number(self):
        self.ensure_one()
        # we supposed that gtin is the input
        if not self.lot_name:
            return
        try:
            result = self.env["gs1_barcode"].decode(self.lot_name)
            product_tmpl_gtin = result.get('01')
            if product_tmpl_gtin != self.product_id.product_tmpl_id.gtin:
                raise UserError(_(
                    'The given GTIN code %s doesn\'t match with the product GTIN code %s') %
                                (product_tmpl_gtin, self.product_id.product_tmpl_id.gtin or ''))
            self.lot_name = result.get("10")
            self.peremption_1 = datetime.strptime(result.get("17"), "%Y-%m-%d")
        except (AttributeError, ValidationError) as e:
            self.peremption_1 = False

    def _action_done(self):
        """ This method is called during a move's `action_done`. It'll actually move a quant from
        the source location to the destination location, and unreserve if needed in the source
        location.

        This method is intended to be called on all the move lines of a move. This method is not
        intended to be called when editing a `done` move (that's what the override of `write` here
        is done.
        """
        Quant = self.env['stock.quant']

        # First, we loop over all the move lines to do a preliminary check: `qty_done` should not
        # be negative and, according to the presence of a picking type or a linked inventory
        # adjustment, enforce some rules on the `lot_id` field. If `qty_done` is null, we unlink
        # the line. It is mandatory in order to free the reservation and correctly apply
        # `action_done` on the next move lines.
        ml_to_delete = self.env['stock.move.line']
        for ml in self:
            # Check here if `ml.qty_done` respects the rounding of `ml.product_uom_id`.
            uom_qty = float_round(ml.qty_done, precision_rounding=ml.product_uom_id.rounding, rounding_method='HALF-UP')
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            qty_done = float_round(ml.qty_done, precision_digits=precision_digits, rounding_method='HALF-UP')
            if float_compare(uom_qty, qty_done, precision_digits=precision_digits) != 0:
                raise UserError(_('The quantity done for the product "%s" doesn\'t respect the rounding precision \
                                  defined on the unit of measure "%s". Please change the quantity done or the \
                                  rounding precision of your unit of measure.') % (
                    ml.product_id.display_name, ml.product_uom_id.name))

            qty_done_float_compared = float_compare(ml.qty_done, 0, precision_rounding=ml.product_uom_id.rounding)
            if qty_done_float_compared > 0:
                if ml.product_id.tracking != 'none':
                    picking_type_id = ml.move_id.picking_type_id
                    if picking_type_id:
                        if picking_type_id.use_create_lots:
                            # If a picking type is linked, we may have to create a production lot on
                            # the fly before assigning it to the move line if the user checked both
                            # `use_create_lots` and `use_existing_lots`.
                            if ml.lot_name and not ml.lot_id:
                                lot = self.env['stock.production.lot'].create(
                                    {'name': ml.lot_name, 'product_id': ml.product_id.id,
                                     'company_id': ml.move_id.company_id.id, 'life_date': ml.peremption_1}
                                )
                                ml.write({'lot_id': lot.id})
                        elif not picking_type_id.use_create_lots and not picking_type_id.use_existing_lots:
                            # If the user disabled both `use_create_lots` and `use_existing_lots`
                            # checkboxes on the picking type, he's allowed to enter tracked
                            # products without a `lot_id`.
                            continue
                    elif ml.move_id.inventory_id:
                        # If an inventory adjustment is linked, the user is allowed to enter
                        # tracked products without a `lot_id`.
                        continue

                    if not ml.lot_id:
                        raise UserError(
                            _('You need to supply a Lot/Serial number for product %s.') % ml.product_id.display_name)
                    # only for outgoing product
                    if ml.picking_code == 'outgoing' and ml.product_id.uom_id.category_id.id == self.env.ref(
                            'uom.product_uom_categ_vol').id:
                        moves_out = self.env['stock.move.line'].search(
                            [('lot_id', '=', ml.lot_id.id), ('picking_code', '=', 'outgoing')])
                        moves_in = self.env['stock.move.line'].search(
                            [('lot_id', '=', ml.lot_id.id), ('picking_code', '=', 'incoming')])

                        def _compute_qty_uom(move_ids):
                            return sum([rec.product_uom_id._compute_quantity(
                                rec.qty_done, rec.move_id.product_id.uom_id, rounding_method='HALF-UP') for rec in
                                move_ids])

                        qty_done_in = _compute_qty_uom(moves_in)
                        qty_done_out = _compute_qty_uom(moves_out)
                        # bottle opened
                        if qty_done_in > qty_done_out:
                            moves_out = sorted(moves_out, key=lambda rec: rec.create_date)
                            # get the create date of the first recordset and update + 30j -> 0 ... 29
                            ml.lot_id.use_date = ml.lot_id.removal_date = moves_out[0].create_date + relativedelta(
                                days=30)
                    if ml.lot_id.life_date:
                        if ml.lot_id.life_date.date() <= fields.Date.today():
                            raise UserError(
                                _('The date on the Lot/Serial has expired')
                            )
                    if ml.lot_id.use_date:
                        if ml.lot_id.use_date.date() <= fields.Date.today():
                            raise UserError(
                                _('The date on the Lot/Serial has expired')
                            )
            elif qty_done_float_compared < 0:
                raise UserError(_('No negative quantities allowed'))
            else:
                ml_to_delete |= ml
        ml_to_delete.unlink()

        (self - ml_to_delete)._check_company()

        # Now, we can actually move the quant.
        done_ml = self.env['stock.move.line']
        for ml in self - ml_to_delete:
            if ml.product_id.type == 'product':
                rounding = ml.product_uom_id.rounding

                # if this move line is force assigned, unreserve elsewhere if needed
                if not ml._should_bypass_reservation(ml.location_id) and float_compare(ml.qty_done, ml.product_uom_qty,
                                                                                       precision_rounding=rounding) > 0:
                    qty_done_product_uom = ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id,
                                                                               rounding_method='HALF-UP')
                    extra_qty = qty_done_product_uom - ml.product_qty
                    ml._free_reservation(ml.product_id, ml.location_id, extra_qty, lot_id=ml.lot_id,
                                         package_id=ml.package_id, owner_id=ml.owner_id, ml_to_ignore=done_ml)
                # unreserve what's been reserved
                if not ml._should_bypass_reservation(
                        ml.location_id) and ml.product_id.type == 'product' and ml.product_qty:
                    try:
                        Quant._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty,
                                                        lot_id=ml.lot_id, package_id=ml.package_id,
                                                        owner_id=ml.owner_id, strict=True)
                    except UserError:
                        Quant._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=False,
                                                        package_id=ml.package_id, owner_id=ml.owner_id, strict=True)

                # move what's been actually done
                quantity = ml.product_uom_id._compute_quantity(ml.qty_done, ml.move_id.product_id.uom_id,
                                                               rounding_method='HALF-UP')
                available_qty, in_date = Quant._update_available_quantity(ml.product_id, ml.location_id, -quantity,
                                                                          lot_id=ml.lot_id, package_id=ml.package_id,
                                                                          owner_id=ml.owner_id)
                if available_qty < 0 and ml.lot_id:
                    # see if we can compensate the negative quants with some untracked quants
                    untracked_qty = Quant._get_available_quantity(ml.product_id, ml.location_id, lot_id=False,
                                                                  package_id=ml.package_id, owner_id=ml.owner_id,
                                                                  strict=True)
                    if untracked_qty:
                        taken_from_untracked_qty = min(untracked_qty, abs(quantity))
                        Quant._update_available_quantity(ml.product_id, ml.location_id, -taken_from_untracked_qty,
                                                         lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id)
                        Quant._update_available_quantity(ml.product_id, ml.location_id, taken_from_untracked_qty,
                                                         lot_id=ml.lot_id, package_id=ml.package_id,
                                                         owner_id=ml.owner_id)
                Quant._update_available_quantity(ml.product_id, ml.location_dest_id, quantity, lot_id=ml.lot_id,
                                                 package_id=ml.result_package_id, owner_id=ml.owner_id, in_date=in_date)
            done_ml |= ml
        # Reset the reserved quantity as we just moved it to the destination location.
        (self - ml_to_delete).with_context(bypass_reservation_update=True).write({
            'product_uom_qty': 0.00,
            'date': fields.Datetime.now(),
        })
