# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    source = fields.Selection([('ounit', 'Operating Unit'), ('phone', 'Phone'), ('web', 'Web')], 'Source', compute='_compute_source',
                              store=True)
    slot_ids = fields.One2many('planning.slot', 'partner_id', 'Planning Slots')
    patient_slot_ids = fields.One2many('planning.slot', 'patient_id', 'Patient Planning Slots')

    @api.depends('slot_ids')
    def _compute_source(self):
        for rec in self:
            if rec.slot_ids:
                rec.source = rec.slot_ids.sorted(key=lambda s: s.create_date)[0].source
            else:
                rec.source = 'ounit'