# -*- coding: utf-8 -*-

from odoo import api, fields, models


class OperatingUnit(models.Model):
    _inherit = 'operating.unit'
    _inherits = {'res.partner': 'partner_id'}

    street = fields.Char(related='partner_id.street', inherited=True, readonly=False)
    street2 = fields.Char(related='partner_id.street2', inherited=True, readonly=False)
    zip = fields.Char(related='partner_id.zip', inherited=True, readonly=False)
    city = fields.Char(related='partner_id.city', inherited=True, readonly=False)
    country_id = fields.Many2one(related='partner_id.country_id', inherited=True, readonly=False)
    state_id = fields.Many2one(related='partner_id.state_id', inherited=True, readonly=False)
    email = fields.Char(related='partner_id.email', inherited=True, readonly=False)
    phone = fields.Char(related='partner_id.phone', inherited=True, readonly=False)
    mobile = fields.Char(related='partner_id.mobile', inherited=True, readonly=False)
    emergency_phone = fields.Char('Emergency Phone')
    type_id = fields.Many2one('operating.unit.type', 'Clinic Type')
    vat = fields.Char(related='partner_id.vat', inherited=True, readonly=False)
    calendar_id = fields.Many2one('resource.calendar', 'Opening Time')
    consult_room_number = fields.Integer('Consultation Rooms Number')
    equipment_ids = fields.Many2many('maintenance.equipment', 'operating_unit_equipment_rel', 'operating_unit_id', 'equipment_id',
                                     'Equipments')
    click_and_collect = fields.Boolean()
    online_appointment_booking = fields.Boolean()
    rooms_ids = fields.One2many('operating.unit.room', 'operating_unit_id', 'Rooms')
    access_reduced_mobility = fields.Boolean()
    parking = fields.Boolean()
    certification_ids = fields.Many2many('operating.unit.certification', 'operating_unit_certification_rel',
                                         'operating_unit_id', 'certification_id', 'Certifications')
    name = fields.Char(related='partner_id.name', inherited=True, readonly=False)
    password = fields.Char('Password')
    argos_code = fields.Char('Argos Code', compute='_compute_argos_code')
    sequence = fields.Char('Sequence', copy=False)

    @api.depends('zip')
    def _compute_argos_code(self):
        for record in self:
            record.argos_code = '-'.join([attr for attr in [record.zip, record.sequence] if attr])

    @api.model
    def default_get(self, fields):
        res = super(OperatingUnit, self).default_get(fields)
        if not res.get('sequence'):
            res.update({'sequence': self.env['ir.sequence'].next_by_code('operating.unit.seq')})
        return res

    def toggle_active(self):
        self.ensure_one()
        if self.active:
            self.active = False
        else:
            self.active = True
        return True

    @api.model
    def _get_operating_unit_by_location(self, location=False):
        return self.search([('name', '=', location)], limit=1)
