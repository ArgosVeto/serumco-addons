# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import UserError

class medical_appointments_invoice_wizard(models.TransientModel):
    _name = "medical.appointments.invoice.wizard"
    
    def create_invoice(self):
        id = self._context.get('active_id')
        lab_req_obj = self.env['medical.appointment']
        account_invoice_obj  = self.env['account.move']
        account_invoice_line_obj = self.env['account.move.line']
        ir_property_obj = self.env['ir.property']

        lab_req = lab_req_obj.browse(id)
        if lab_req.is_invoiced == True:
            raise UserError(_(' Invoice is Already Exist'))
        if lab_req.no_invoice == False:
            
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
                            'views': [ [form_view_id,'form' ]],
                            'target': action.target,
                            'context': action.context,
                            'res_model': action.res_model,
                            'res_id':res.id,
                            }
                if res:
                    result['domain'] = "[('id','=',%s)]" % res.id
        else:
             raise UserError(_(' The Appointment is invoice exempt   '))
        return result

