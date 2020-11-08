# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from odoo import models, fields, api

fields_to_export = ['name', 'species_id', 'race_id', 'gender_id', 'robe_id', 'birthdate_date', 'age_formatted', 'weight', 'passport_id',
                    'tattoo_number', 'chip_identification', 'employee_id', 'operating_unit_id', 'display_name', 'phone', 'email', 'city',
                    'state_id', 'country_id', 'image', 'consultation_ids', 'owner_ids', 'result_line_ids']


class ExportMedicalHistory(models.TransientModel):
    _name = 'export.medical.history'

    @api.model
    def get_fields(self):
        return self.env['ir.model.fields'].search([('name', 'in', fields_to_export),
                                                   ('model_id.model', '=', 'res.partner')]).ids

    field_ids = fields.Many2many('ir.model.fields', 'res_partner_fields_rel', 'partner_id', 'fields_id', string='Fields To Export',
                                 domain="[('name','in', ['name', 'species_id', 'race_id', 'gender_id', 'robe_id', "
                                        "'birthdate_date', 'age_formatted', 'weight', 'passport_id', 'tattoo_number', "
                                        "'chip_identification', 'employee_id', 'operating_unit_id', 'image', 'consultation_ids', "
                                        "'owner_ids', 'result_line_ids']),"
                                        "('model_id.model', '=', 'res.partner')]",
                                 default=get_fields)

    is_complete = fields.Boolean('Is Complete', default=True)
    date_start = fields.Date('Start Date', required=True)
    date_end = fields.Date('End Date', required=True)
    partner_id = fields.Many2one('res.partner', 'Animal', readonly=True)

    @api.onchange('is_complete')
    def onchange_is_complete(self):
        if self.is_complete:
            self.field_ids = self.env['ir.model.fields'].search([('name', 'in', fields_to_export),
                                                                 ('model_id.model', '=', 'res.partner')]).ids


    @api.model
    def default_get(self, fields_list):
        res = super(ExportMedicalHistory, self).default_get(fields_list)
        if not res.get('partner_id'):
            res.update({'partner_id': self._context.get('active_id')})
        return res

    def button_print_report(self):
        self.ensure_one()
        consultations = self.partner_id.consultation_ids.filtered(
            lambda cons: cons.consultation_date >= self.date_start and cons.consultation_date <= self.date_end)
        data = {
            'partner': self.partner_id.read(fields=fields_to_export)[0],
            'owners': self.partner_id.owner_ids.read(fields=['display_name', 'country_id', 'city', 'phone', 'email']),
            'consultations': consultations.read(fields=['consultation_date', 'patient_id', 'employee_id', 'diagnostic_ids',
                                                        'hypothese_ids', 'operating_unit_id']),
            'analysis': self.partner_id.result_line_ids.read(fields=['result_date', 'parameter_id', 'value', 'min', 'max', 'unit',
                                                                     'comments']),
            'date_start': self.date_start,
            'date_end': self.date_end,
            'fields_to_print': self.field_ids.mapped('name'),
        }
        return self.env.ref('argos_contact.export_medical_history_report').report_action(self, data=data)
