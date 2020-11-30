
from odoo import api, models
from odoo.tools import float_is_zero


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder)
        for move in res:
            if move.product_id.valuation != 'real_time':
                if not move.force_entry():
                    continue
            if not move._is_internal():
                continue
            svl = move._create_internal_svl()
            if float_is_zero(svl.value, precision_digits=self.env.company.currency_id.rounding):
                continue
            move._account_entry_move(svl.quantity, svl.description, svl.id, svl.value)
        return res

    def force_entry(self):
        """
        Inherit to force internal entry
        :return:
        """
        self.ensure_one()
        return False

    def _account_entry_move(self, quantity, description, svl_id, value):
        self.ensure_one()
        res = super()._account_entry_move(quantity, description, svl_id, value)
        if res is not None and not res:
            return res
        self = self.with_context(forced_quantity=-self.product_qty)

        location_from = self.location_id
        location_to = self.location_dest_id

        if self._is_internal():
            product_valuation_accounts = self.product_id.product_tmpl_id.get_product_accounts()
            stock_valuation = product_valuation_accounts.get('stock_valuation')
            stock_journal = product_valuation_accounts.get('stock_journal')

            if location_from.force_accounting_entries and location_to.force_accounting_entries:
                self._create_account_move_line(
                    location_from.valuation_out_account_id.id,
                    location_to.valuation_in_account_id.id,
                    stock_journal.id, quantity, description, svl_id, value)
            elif location_from.force_accounting_entries:
                self._create_account_move_line(
                    location_from.valuation_out_account_id.id,
                    stock_valuation.id,
                    stock_journal.id, quantity, description, svl_id, value)
            elif location_to.force_accounting_entries:
                self._create_account_move_line(
                    stock_valuation.id,
                    location_to.valuation_in_account_id.id,
                    stock_journal.id, quantity, description, svl_id, value)

        return res

    def _is_internal(self):
        self.ensure_one()
        return self.location_id.usage == 'internal' and self.location_dest_id.usage == 'internal'

    def _prepare_internal_svl_vals(self, quantity):
        self.ensure_one()
        vals = {
            'product_id': self.id,
            'value': quantity * self.standard_price,
            'unit_cost': self.standard_price,
            'quantity': quantity,
        }
        return vals

    def _get_internal_move_lines(self):
        self.ensure_one()
        res = self.env['stock.move.line']
        for move_line in self.move_line_ids:
            if move_line.owner_id and move_line.owner_id != move_line.company_id.partner_id:
                continue
            if move_line.location_id._should_be_valued() and move_line.location_dest_id._should_be_valued():
                res |= move_line
        return res

    def _create_internal_svl(self, forced_quantity=None):
        svl_vals_list = []
        for move in self:
            move = move.with_context(force_company=move.company_id.id)
            valued_move_lines = move._get_internal_move_lines()
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, move.product_id.uom_id)
            unit_cost = move.product_id.standard_price
            svl_vals = move.product_id._prepare_internal_svl_vals(forced_quantity or valued_quantity, unit_cost)
            svl_vals.update(move._prepare_common_svl_vals())
            svl_vals_list.append(svl_vals)
        return self.env['stock.valuation.layer'].sudo().create(svl_vals_list)
