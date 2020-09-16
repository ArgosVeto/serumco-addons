# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    patient_id = fields.Many2one('res.partner', 'Patient')

    def _query(self, with_clause='', fields=False, groupby='', from_clause=''):
        if not fields:
            fields = {}
        fields['patient_id'] = ', s.patient_id as patient_id'
        groupby += ', s.patient_id'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)