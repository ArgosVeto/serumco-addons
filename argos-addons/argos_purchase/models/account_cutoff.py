# -*- coding: utf-8 -*-

from odoo import models, fields, _


class AccountCutoff(models.Model):
    _inherit = 'account.cutoff'

    purchase_cutoff = fields.Boolean('Purchase Cutoff', readonly=True, help='Used for a single purchase order cutoff')

    _sql_constraints = [
        (
            "date_type_company_uniq",
            "CHECK(purchase_cutoff != true AND UNIQUE(cutoff_date, company_id, cutoff_type))",
            _("A cutoff of the same type already exists with this cut-off date !"),
        )
    ]
