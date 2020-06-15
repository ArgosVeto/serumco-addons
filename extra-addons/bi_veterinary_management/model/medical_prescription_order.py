# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime

class medical_prescription_order(models.Model):
    
    _name = "medical.prescription.order"
    
    name = fields.Char('Prescription ID')
    
    patient_id = fields.Many2one('medical.patient','Patient ID')
    owner_name_id = fields.Many2one('res.partner', 'Owner Name')
    prescription_date = fields.Datetime('Prescription Date', default=fields.Datetime.now)
    user_id = fields.Many2one('res.users','Log In User', default=lambda self: self.env.user)
    no_invoice = fields.Boolean('Invoice exempt')
    inv_id = fields.Many2one('account.invoice','Invoice',copy=False)
    doctor_id = fields.Many2one('medical.physician','Prescribing Doctor')
    medical_appointment_id = fields.Many2one('medical.appointment','Appointment')
    state = fields.Selection([('invoiced','To Invoiced'),('tobe','To Be Invoiced')], 'Invoice Status',copy=False)
    pharmacy_partner_id = fields.Many2one('res.partner', 'Pharmacy')
    prescription_line_ids = fields.One2many('medical.prescription.line','name','Prescription Line')
    invoice_done= fields.Boolean('Invoice Done',copy=False)
    notes = fields.Text('Prescription Note')
    appointment_id = fields.Many2one('medical.appointment')
    is_invoiced = fields.Boolean(default  = False,copy=False)
    is_shipped = fields.Boolean(default  =  False,copy=False)
    
    @api.onchange('patient_id')
    def on_change_patient_id(self):   
        self.owner_name_id = self.patient_id.patient_id.owner_id

    @api.model
    def create(self , vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('medical.prescription.order') or '/'
        return super(medical_prescription_order, self).create(vals)
    
    @api.onchange('name')
    def onchange_name(self):
        self.pricelist_id = 1 or False
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
