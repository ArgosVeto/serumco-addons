# -*- coding: utf-8 -*-

from collections import defaultdict
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
        group = values and values[0].get('group_id', False)
        if group and getattr(group, 'sale_id', False) and getattr(group.sale_id, 'website_id', False):
            res.update({'from_website': True})
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

    @api.model
    def _run_buy(self, procurements):
        super(StockRule, self)._run_buy(procurements)
        procurements_by_po_domain = defaultdict(list)
        for procurement, rule in procurements:
            supplier = procurement.product_id.with_context(force_company=procurement.company_id.id)._select_seller(
                partner_id=procurement.values.get("supplier_id"),
                quantity=procurement.product_qty,
                uom_id=procurement.product_uom)
            domain = rule._make_po_get_domain(procurement.company_id, procurement.values, supplier.name)
            procurements_by_po_domain[domain].append((procurement, rule))
        for domain, procurements_rules in procurements_by_po_domain.items():
            purchase = self.env['purchase.order'].sudo().search([dom for dom in domain], limit=1)
            if purchase:
                purchase.button_confirm()