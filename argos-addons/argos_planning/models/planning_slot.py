# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class PlanningSlot(models.Model):
    _inherit = 'planning.slot'

    mrdv_event_id = fields.Integer('Mrdv Id')
    mrdv_job_id = fields.Integer('Mrdv Job Id')
    source = fields.Selection([('odoo', 'Odoo'), ('mrdv', 'Mrdv')], 'Source', default='odoo')
    animal_id = fields.Many2one('animal.animal', 'Animal')
    partner_id = fields.Many2one('res.partner', 'Customer')
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')
    consultation_type_id = fields.Many2one('consultation.type', 'Consultation Type')
    active = fields.Boolean('Active', default=True)
    state = fields.Selection([('draft', 'Draft'), ('validated', 'Validated'), ('cancel', 'Cancelled')], 'State',
                             default='draft')
    more_info = fields.Text('More Information')

    @api.model
    def _cron_recover_planning(self):
        self._recover_away()
        self._recover_presence()
        self.env['planning.assignment']._recover_assignment()

    @api.model
    def _recover_away(self):
        print('Away')

    @api.model
    def _recover_presence(self):
        print('Presence')

    @api.model
    def _prepare_slot_data(self, post={}):
        if not post:
            return {}
        return {
            'mrdv_event_id': post.get('mrdvEventId'),
            'mrdv_job_id': post.get('mrdvJobId'),
            'source': 'mrdv',
            'role_id': self.env['planning.role']._get_role_by_type(post.get('type')).id,
            'name': post.get('title'),
            'state': post.get('status'),
            'more_info': post.get('CustomerMoreInfo'),
            'start_datetime': post.get('startDate'),
            'end_datetime': post.get('endDate'),
            'consultation_type_id': self.env['consultation.type']._get_consultation_type(
                post.get('consultationName')).id,
            'operating_unit_id': self.env['operating.unit']._get_operating_unit_by_location(post.get('location')).id,
            'partner_id': self.env['res.partner']._get_partner_by_name(post.get('customerName'),
                                                                       post.get('customerPhone')).id,
            'animal_id': self.env['animal.animal']._get_animal_by_name(post.get('petName'), post.get('animalName'),
                                                                       post.get('customerName'),
                                                                       post.get('customerPhone')).id,
        }

    def validate(self):
        self.write({'state': 'validated'})

    def cancel(self):
        self.write({'state': 'cancel'})

    def set_to_draft(self):
        self.write({'state': 'draft'})

    def toggle_active(self):
        for rec in self:
            if rec.active:
                rec.cancel()
        super(PlanningSlot, self).toggle_active()
