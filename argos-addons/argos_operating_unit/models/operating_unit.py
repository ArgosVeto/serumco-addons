# -*- coding: utf-8 -*-

from odoo import api, fields, models


class OperatingUnit(models.Model):
    _inherit = ['operating.unit']

    address = fields.Char('Address', related='partner_id.contact_address')
    email = fields.Char(related='partner_id.email')
    principal_phone = fields.Char('Principal Phone')
    secondary_phone = fields.Char('Secondary Phone')
    emergency_phone = fields.Char('Emergency Phone')
    type_id = fields.Many2one('operating.unit.type', 'Clinic Type')
    vat = fields.Char(related='partner_id.vat')
    opening_time = fields.Char('Opening Time')
    consult_room_number = fields.Integer('Consultation Rooms Number')
    skill_ids = fields.Many2many('documents.tag', 'operating_unit_document_tag_rel', 'operating_unit_id', 'tag_id', 'Skills List')
    equipment_ids = fields.Many2many('maintenance.equipment', 'operating_unit_equipment_rel', 'operating_unit_id', 'equipment_id', 'Equipments')
    click_and_collect = fields.Boolean()
    ecommerce_relay_point = fields.Boolean()
    online_appointment_booking = fields.Boolean()

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
