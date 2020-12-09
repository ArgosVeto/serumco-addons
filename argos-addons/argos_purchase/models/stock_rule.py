# -*- coding: utf-8 -*-

from odoo import models, api, fields


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', related='sale_id.operating_unit_id')

    @api.model
    def run(self, procurements):
        for procurement in procurements:
            if procurement.values and procurement.values.get('group_id', False) and procurement.values['group_id'].operating_unit_id:
                procurement.values['operating_unit_id'] = procurement.values['group_id'].operating_unit_id
        return super(ProcurementGroup, self).run(procurements)


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_purchase_order(self, company_id, origins, values):
        res = super(StockRule, self)._prepare_purchase_order(company_id, origins, values)
        group = res.get('group_id', False)
        if group and group.operating_unit_id:
            operating_unit = group.operating_unit_id
            type_obj = self.env['stock.picking.type']
            type = type_obj.search([("code", "=", "incoming"), ("warehouse_id.operating_unit_id", "=", operating_unit.id)], limit=1)
            if type:
                res.update({'picking_type_id': type.id, 'operating_unit_id': operating_unit.id})
        return res

    def _make_po_get_domain(self, company_id, values, partner):
        dom = super(StockRule, self)._make_po_get_domain(company_id, values, partner)
        if values.get('operating_unit_id', False):
            dom += (('operating_unit_id', '=', values.get('operating_unit_id').id),)
        return dom

    @api.model
    def _get_procurements_to_merge_groupby(self, procurement):
        return procurement.values.get('operating_unit_id'), super(StockRule, self)._get_procurements_to_merge_groupby(procurement)

    @api.model
    def _get_procurements_to_merge_sorted(self, procurement):
        return procurement.values.get('operating_unit_id'), super(StockRule, self)._get_procurements_to_merge_sorted(procurement)