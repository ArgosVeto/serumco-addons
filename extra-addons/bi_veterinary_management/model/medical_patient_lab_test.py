# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime
# classes under  menu of laboratry 


class medical_patient_lab_test(models.Model):
    _name = 'medical.patient.lab.test'

    request = fields.Char('Request', readonly = True)
    date =  fields.Datetime('Date', default = datetime.now())
    bi_owner_id = fields.Many2one('res.partner', 'Owner Name')
    
    urgent =  fields.Boolean('Urgent',)
    owner_id = fields.Many2one('res.partner', required = True,string="Owner")
     
    state = fields.Selection([('draft', 'Draft'),('tested', 'Tested'), ('cancel', 'Cancel')], readonly= True, default = 'draft')
    name = fields.Many2one('medical.test_type', 'Test',required = True)
    patient_id = fields.Many2one('medical.patient','Patient' )
    doctor_id = fields.Many2one('medical.physician','Doctor',required= True)
    urgent = fields.Boolean('Urgent')
    lab_res_created = fields.Boolean(default  =  False) 
    is_invoiced = fields.Boolean(default  =  False,copy=False)
    
    @api.onchange('patient_id')
    def on_change_patient_id(self):   
        self.owner_id = self.patient_id.patient_id.owner_id
             
    @api.model
    def create(self, vals):
        vals['request'] = self.env['ir.sequence'].next_by_code('test_seq')
        result = super(medical_patient_lab_test, self).create(vals)
        return result 
    
    
    def create_lab_test(self):
        res_ids = []
        for browse_record in self:
            result = {}
            medical_lab_obj = self.env['medical.lab']
            res = medical_lab_obj.create({'name': browse_record.name,
                                       'patient_id': browse_record.patient_id.id or False,
                                       'date_requested':browse_record.date or False,
                                       'medical_test_type_id':browse_record.name.id or False,
                                       'requestor_physician_id': browse_record.doctor_id.id or False,
                                       })
            res_ids.append(res.id)
            if res_ids:                     
                imd = self.env['ir.model.data']
                action = imd.xmlid_to_object('bi_veterinary_management.action_view_lab_results_tree')
                list_view_id = imd.xmlid_to_res_id('bi_veterinary_management.bi_view_medical_lab_tree')
                form_view_id  =  imd.xmlid_to_res_id('bi_veterinary_management.view_medical_lab_form')

                result = {
                                'name': action.name,
                                'help': action.help,
                                'type': action.type,
                                'views': [ [list_view_id,'tree' ],[form_view_id,'form']],
                                'target': action.target,
                                'context': action.context,
                                'res_model': action.res_model,
                                'res_id':res.id,
                            }
        if res_ids:
            result['domain'] = "[('id','=',%s)]" % res_ids

        return result


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    