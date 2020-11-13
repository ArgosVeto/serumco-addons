# -*- coding: utf-8 -*-

from odoo import fields, models, api


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

    @api.depends('initial_qty', 'delivered_qty', 'qty_done')
    def _compute_remaining_qty(self):
        for line in self:
            line.remaining_qty = line.initial_qty - (line.delivered_qty + line.qty_done)
