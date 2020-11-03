# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleCouponProgram(models.Model):
    _inherit = 'sale.coupon.program'

    @api.model
    def _filter_promotion_programs_from_product(self, order, product):
        programs = self.search([('program_type', '=', 'promotion_program')])._filter_on_validity_dates(order)
        valid_programs = programs.filtered(lambda program: program._is_valid_product(product))
        return valid_programs
