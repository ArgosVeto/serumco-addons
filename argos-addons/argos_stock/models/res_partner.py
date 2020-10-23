# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'
    picking_ids = fields.Many2many('stock.picking', 'Prescriptions', compute='_compute_prescription_patient')

    def _compute_prescription_patient(self):
        for partner in self:
            orders = self.env['sale.order'].search([('patient_id', '=', partner.id)])
            pickings = orders.picking_ids.filtered(lambda p: p.is_arg_prescription)
            partner.picking_ids = [(6, 0, pickings.ids)]
