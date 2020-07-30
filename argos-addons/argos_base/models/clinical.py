# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class Animal(models.Model):
    _name = "clinical.clinical"
    _description = "Clinical"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name')
    operating_unit_id = fields.Many2one('operating.unit', 'Partner')
    clinical_code = fields.Char('Clinical Code', related='operating_unit_id.code')
    address = fields.Char('Address', related='operating_unit_id.partner_id.contact_address')
    email = fields.Char('Email', related='operating_unit_id.partner_id.email')
    principal_phone = fields.Char('Principal Phone')
    secondary_phone = fields.Char('Secondary Phone')
    emergency_phone = fields.Char('Emergency Phone')
    clinical_type_id = fields.Many2one('clinical.type', 'Clinical Type')
    vat = fields.Char('Vat')
    opening_time = fields.Char('Opening Time')
    consult_room_number = fields.Integer('Consultation Rooms Number')
    skill_ids = fields.Many2many('documents.tag', string='Skills List')
    equipment_ids = fields.Many2many('maintenance.equipment', string='Equipments')
    click_and_collect = fields.Boolean()
    ecommerce_relay_point = fields.Boolean()
    online_appointment_booking = fields.Boolean()