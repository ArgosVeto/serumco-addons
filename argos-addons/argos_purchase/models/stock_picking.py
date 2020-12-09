# -*- coding: utf-8 -*-

from odoo.exceptions import Warning
from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.depends()
    def _compute_state(self):
        super(StockPicking, self)._compute_state()
        for picking in self:
            if picking.state == 'done' and picking.picking_type_code == 'incoming':
                moves = picking.move_lines.filtered(lambda move: move.state == "done")
                purchase = moves.mapped('purchase_line_id').mapped('order_id')
                if purchase and len(purchase) == 1:
                    cutoff_account = self.env.company.default_accrued_expense_account_id
                    cutoff_account = cutoff_account or self.env['account.account'].search([('code', '=', '408100')], limit=1)
                    picking.create_purchase_cutoff(purchase, cutoff_account)
                    if not purchase.invoice_ids:
                        invoice = picking.create_purchase_invoice({'purchase_id': purchase.id, 'type': 'in_invoice', 'company_id':
                            picking.company_id.id})
                        purchase.invoice_ids = invoice

    @api.model
    def create_purchase_cutoff(self, purchase, cutoff_account):
        account_cutoff_obj = self.env['account.cutoff']
        account_cutoff_line_obj = self.env['account.cutoff.line']
        cutoff_journal = self.env['account.journal'].search([('company_id', '=', self.company_id.id), ('type', '=', 'purchase')], limit=1)
        if not cutoff_journal:
            raise Warning(_('Please configure a vendor journal for %s' % self.company_id.name))
        if not cutoff_account:
            raise Warning(_('Unable to find the account %s for accrued expense' % cutoff_account.code))
        cutoff_values = self._prepare_purchase_cutoff(cutoff_account, cutoff_journal, self.company_id, purchase.name)
        cutoff = account_cutoff_obj.create(cutoff_values)
        cutoff_lines_values = self._prepare_purchase_cutoff_line(cutoff)
        account_cutoff_line_obj.create(cutoff_lines_values)
        cutoff.create_move()
        if cutoff.move_id:
            cutoff.move_id.action_post()
        purchase.write({'cutoff_id': cutoff.id, 'cutoff_move_ids': [(4, cutoff.move_id.id)]})
        return True

    def _prepare_purchase_cutoff(self, account, journal, company, origin='', type='accrued_expense'):
        return {
            'cutoff_account_id': account.id,
            'cutoff_journal_id': journal.id,
            'company_id': company.id,
            'cutoff_type': type,
            'cutoff_date': fields.Date.today(),
            'move_label': origin,
            'purchase_cutoff': True
        }

    def _prepare_purchase_cutoff_line(self, cutoff):
        account_cutoff_mapping_obj = self.env['account.cutoff.mapping']
        account_mapping = account_cutoff_mapping_obj._get_mapping_dict(self.company_id.id, type)
        purchase_line_dict = {}
        line_values = {}
        for move in self.move_lines.filtered(lambda move: move.state == "done"):
            cutoff.stock_move_update_oline_dict(move, purchase_line_dict)
        for val in purchase_line_dict.values():
            line_values = cutoff.picking_prepare_cutoff_line(val, account_mapping)
        return line_values

    def create_purchase_invoice(self, vals):
        invoice = self.env["account.move"].new(vals)
        invoice._onchange_purchase_auto_complete()
        return invoice
