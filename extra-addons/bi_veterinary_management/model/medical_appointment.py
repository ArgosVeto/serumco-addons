# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import UserError


class medical_appointment(models.Model):
    _name = "medical.appointment"

    name = fields.Char(string="Appointment ID", readonly=True)
    is_invoiced = fields.Boolean(default = False,copy=False)
    institution_id = fields.Many2one('res.partner',string="Health Center")
    inpatient_registration_code_id = fields.Many2one('medical.inpatient.registration',string="Inpatient Registration")
    patient_status = fields.Selection([
            ('ambulatory', 'Ambulatory'),
            ('outpatient', 'Outpatient'),
            ('inpatient', 'Inpatient'),
        ], 'Patient status', sort=False,default='ambulatory')
    patient_id = fields.Many2one('medical.patient','Patient',required=True)
    urgency = fields.Selection([
            ('a', 'Normal'),
            ('b', 'Urgent'),
            ('c', 'Medical Emergency'),
        ], 'Urgency Level', sort=False,default="b")
    appointment_start_date = fields.Datetime('Appointment Start',required=True,default = datetime.now())
    appointment_end_date = fields.Datetime('Appointment End',required=True)
    doctor_id = fields.Many2one('medical.physician','Physician',required=True)
    speciality_id = fields.Many2one('medical.speciality','Speciality')
    no_invoice = fields.Boolean(string='Invoice exempt',default=True)
    validity_status = fields.Selection([
            ('invoice', 'Invoice'),
            ('tobe', 'To be Invoiced'),
        ], 'Status', sort=False,readonly=True,default='tobe')
    appointment_validity_date = fields.Datetime('Validity Date')
    consultation_id = fields.Many2one('product.product','Consultation Service',required=True)
    comments = fields.Text(string="Info")
    state = fields.Selection([('draft','Draft'),('confirmed','Confirm'),('cancel','Cancel'),('done','Done')],string="State",default='draft')

    pediatrics_ids = fields.Many2many('medical.patient.psc',string='Pediatrics Symptoms Checklist')
    prescription_ids = fields.One2many('medical.prescription.order','appointment_id',string='Prescription')
    owner_name = fields.Many2one('res.partner','Owner')
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('medical.appointment') or 'APT'
        result = super(medical_appointment, self).create(vals)
        return result
    
    
    @api.onchange('doctor_id')
    def onchange_doctor(self):
        if not self.doctor_id:
            self.speciality_id = ""
        doc = self.env['medical.speciality'].browse(self.doctor_id.id)
        self.speciality_id = doc.id
        
    @api.onchange('inpatient_registration_code_id')
    def onchange_patient(self):
        if not self.inpatient_registration_code_id:
            self.patient_id = ""
        inpatient_obj = self.env['medical.inpatient.registration'].browse(self.inpatient_registration_code_id.id)
        self.patient_id = inpatient_obj.id
        
    @api.constrains('appointment_start_date','appointment_end_date')
    def check_date(self):
        for obj in self:
            start_date = obj.appointment_start_date
            end_date = obj.appointment_end_date
 
            if start_date and end_date:
                DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"  ## Set your date format here
                from_dt = start_date
                to_dt = end_date
 
                if to_dt < from_dt:
                    return False
        return True
    
    @api.onchange('patient_id')
    def on_change_patient_id(self):   
        self.owner_name = self.patient_id.patient_id.owner_id
 
    _constraints = [
        (check_date, 'Appointment Start Date must be before Appointment End Date ! ', ['appointment_start_date','appointment_end_date']),
    ]
    
    def confirm(self):
        self.write({'state': 'confirmed'})
        
    def done(self):
        self.write({'state': 'done'})
        
    def cancel(self):
        self.write({'state': 'cancel'})

    def view_patient_invoice(self):
        self.write({'state': 'cancel'})
    
    def create_invoice(self):
        lab_req_obj = self.env['medical.appointment']
        account_invoice_obj  = self.env['account.move']
        account_invoice_line_obj = self.env['account.move.line']
        ir_property_obj = self.env['ir.property']

        lab_req = self and self[0]
        
        if lab_req.no_invoice:
            raise UserError(_(' The Appointment is invoice exempt'))
        
        if lab_req.is_invoiced:
            raise UserError(_(' Invoice is Already Exist'))
        else:
            
            sale_journals = self.env['account.journal'].search([('type','=','sale')])
            invoice_vals = {
                'name': "Customer Invoice",
                'invoice_origin': lab_req.name or '',
                'type': 'out_invoice',
                'ref': False,
                'journal_id':sale_journals and sale_journals[0].id or False,
                'partner_id': lab_req.owner_name.id or False,
                'currency_id':lab_req.owner_name.currency_id.id ,
                'invoice_payment_term_id': False,
                'fiscal_position_id': lab_req.owner_name.property_account_position_id.id,
                'invoice_date': date.today(),
                'company_id':lab_req.owner_name.company_id.id or False ,
            }
        
            res = account_invoice_obj.create(invoice_vals)
            
            invoice_line_account_id = False
            if lab_req.consultation_id.id:
                invoice_line_account_id = lab_req.consultation_id.property_account_income_id.id or lab_req.consultation_id.categ_id.property_account_income_categ_id.id or False 
            if not invoice_line_account_id:
                inc_acc = ir_property_obj.get('property_account_income_categ_id', 'product.category')
            if not invoice_line_account_id:
                raise UserError(
                    _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                    (lab_req.consultation_id.name,))
            
            tax_ids = []
            taxes = lab_req.consultation_id.taxes_id.filtered(lambda r: not lab_req.consultation_id.company_id or r.company_id == lab_req.consultation_id.company_id)
            tax_ids = taxes.ids
                
            invoice_line_vals = {
                'name': lab_req.consultation_id.display_name or '',
                'account_id': invoice_line_account_id,
                'price_unit':lab_req.consultation_id.lst_price,
                'product_uom_id': lab_req.consultation_id.uom_id.id,
                'quantity': 1,
                'product_id':lab_req.consultation_id.id ,
                'move_id': res.id,
                'tax_ids': [(6, 0, tax_ids)],
            }
            res1 = res.write({'invoice_line_ids' :([(0,0,invoice_line_vals)]) })
            if res:
                lab_req.write({'is_invoiced':True})
                imd = self.env['ir.model.data']
                action = imd.xmlid_to_object('account.action_move_out_invoice_type')
                form_view_id = imd.xmlid_to_res_id('account.view_move_form')
                result = {
                            'name': action.name,
                            'help': action.help,
                            'type': action.type,
                            'views': [[form_view_id,'form' ]],
                            'target': action.target,
                            'context': action.context,
                            'res_model': action.res_model,
                            'res_id':res.id,
                            }
                result['domain'] = "[('id','=',%s)]" % res.id
        return result

        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: