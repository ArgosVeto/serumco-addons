# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    source = fields.Selection([('ounit', 'Operating Unit'), ('phone', 'Phone'), ('web', 'Web')], 'Source',
                              compute='_compute_source',
                              store=True)
    slot_ids = fields.One2many('planning.slot', 'partner_id', 'Planning Slots')
    patient_slot_ids = fields.One2many('planning.slot', 'patient_id', 'Patient Planning Slots')
    planning_count = fields.Integer(string='Planning Count', compute='_compute_planning_count')

    @api.depends('slot_ids')
    def _compute_source(self):
        for rec in self:
            if rec.slot_ids:
                rec.source = rec.slot_ids.sorted(key=lambda s: s.create_date)[0].source
            else:
                rec.source = 'ounit'

    @api.depends('slot_ids', 'patient_slot_ids', 'contact_type')
    def _compute_planning_count(self):
        for rec in self:
            rec.planning_count = len(rec.slot_ids)
            if rec.contact_type == 'patient':
                rec.planning_count = len(rec.patient_slot_ids)

    def action_open_planning(self):
        self.ensure_one()
        context = {'agenda_calendar': True, 'column': 'employee_id'}
        if self.contact_type == 'patient':
            action_domain = [('patient_id', '=', self.id)]
            context['default_patient_id'] = self.id

        else:
            action_domain = [('partner_id', '=', self.id)]
            context['default_partner_id'] = self.id
        context['default_employee_id'] = self.employee_id and self.employee_id.id or False
        context['default_operating_unit_id'] = self.operating_unit_id and self.operating_unit_id.id or False
        return {
            'name': _('Planning'),
            'domain': action_domain,
            'context': context,
            'view_mode': 'tree,calendar,form',
            'res_model': 'planning.slot',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
