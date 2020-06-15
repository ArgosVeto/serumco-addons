# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date
from odoo.exceptions import Warning

class create_prescription_invoice(models.TransientModel):

    _name = 'create.prescription.invoice'

    def create_prescription_invoice(self):
        active_id = self._context.get('active_id')
        lab_req_obj = self.env['medical.prescription.order']
        account_invoice_obj  = self.env['account.move']
        account_invoice_line_obj = self.env['account.move.line']
        ir_property_obj = self.env['ir.property']
        
        lab_req = lab_req_obj.browse(active_id)
        if lab_req.is_invoiced:
            raise Warning('All ready Invoiced.')

        sale_journals = self.env['account.journal'].search([('type','=','sale')])
        invoice_vals = {
            'name': "Customer Invoice",
            'invoice_origin': lab_req.name or '',
            'type': 'out_invoice',
            'ref': False,
            'journal_id':sale_journals and sale_journals[0].id or False,
            'partner_id': lab_req.owner_name_id.id or False,
            'currency_id':lab_req.owner_name_id.currency_id.id ,
            'invoice_payment_term_id': False,
            'fiscal_position_id': lab_req.owner_name_id.property_account_position_id.id,
            'team_id': False,
            'invoice_date': date.today(),
            'company_id':lab_req.owner_name_id.company_id.id or False ,
        }
    
        res = account_invoice_obj.create(invoice_vals)
        list_of_vals=[]
        for p_line in lab_req.prescription_line_ids: 
            
            invoice_line_account_id = False
            if p_line.medicament_id.product_id.id:
                invoice_line_account_id = p_line.medicament_id.product_id.property_account_income_id.id or p_line.medicament_id.product_id.categ_id.property_account_income_categ_id.id or False 
            if not invoice_line_account_id:
                invoice_line_account_id = ir_property_obj.get('property_account_income_categ_id', 'product.category')
            if not invoice_line_account_id:
                raise UserError(
                    _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                    (p_line.medicament_id.product_id.name,))
            
            tax_ids = []
            taxes = p_line.medicament_id.product_id.taxes_id.filtered(lambda r: not p_line.medicament_id.product_id.company_id or r.company_id == p_line.medicament_id.product_id.company_id)
            tax_ids = taxes.ids
                
            invoice_line_vals = {
                'name': p_line.medicament_id.product_id.display_name or '',
                'account_id': invoice_line_account_id,
                'price_unit':p_line.medicament_id.product_id.lst_price,
                'product_uom_id': p_line.medicament_id.product_id.uom_id.id,
                'quantity': 1,
                'product_id':p_line.medicament_id.product_id.id ,
                'move_id': res.id,
                'tax_ids': [(6, 0, tax_ids)],
            }
            list_of_vals.append((0,0,invoice_line_vals))
        res1 = res.write({'invoice_line_ids' : list_of_vals})
            
        if res:       
            lab_req.write({'is_invoiced':True,'inv_id':res.id})              
            imd = self.env['ir.model.data']
            lab_req.write({'is_invoiced': True})
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
            if res:
                result['domain'] = "[('id','=',%s)]" % res.id
                    
        return result  
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
