# -*- coding: utf-8 -*-
from odoo import api, models


class Website(models.Model):
    _inherit = 'website'

    def _prepare_sale_order_values(self, partner, pricelist):
        self.ensure_one()
        res = super(Website, self)._prepare_sale_order_values(partner, pricelist)
        operating_unit = self.env['operating.unit'].sudo().search([('click_and_collect', '=', True)], limit=1)
        if operating_unit:
            res['team_id'] = False
            warehouse = self.env['stock.warehouse'].sudo().search([('operating_unit_id', '=', operating_unit.id)], limit=1)
            if warehouse:
                res.update({'team_id': False,
                            'warehouse_id': warehouse.id,
                            'operating_unit_id': operating_unit.id,
                            'company_id': operating_unit.company_id.id})
        return res
