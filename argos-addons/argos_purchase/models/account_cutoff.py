# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class AccountCutoff(models.Model):
    _inherit = 'account.cutoff'

    purchase_cutoff = fields.Boolean('Purchase Cutoff', readonly=True, help='Used for a single purchase order cutoff')

    # _sql_constraints = [
    #     (
    #         "date_type_company_uniq",
    #         "CHECK(1=1)",
    #         _("A cutoff of the same type already exists with this cut-off date !"),
    #     )
    # ]
    #
    # @api.constrains('cutoff_account_id')
    # def check_unique_cutoffdate(self):
    #     for rec in self:
    #         existing_cutoff = self.search([('cutoff_date', '=', rec.cutoff_date), ('company_id', '=', rec.company_id.id),
    #                                        ('cutoff_type', '=', rec.cutoff_type), ('id', '!=', rec.id)], limit=1)
    #         if not rec.purchase_cutoff and existing_cutoff:
    #             raise ValidationError(_('A cutoff of the same type already exists with this cut-off date !'))
