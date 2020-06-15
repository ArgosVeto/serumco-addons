# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime
# classes under  menu of laboratry 

class medical_lab_test_create(models.TransientModel):
    
    _name = 'medical.lab.test.create'
    
    def create_lab_test(self):
        res_ids = []
        lab_rqu_obj = self.env['medical.patient.lab.test']
            
        browse_record = lab_rqu_obj.browse(self._context.get('active_id'))
        result = {}
        medical_lab_obj = self.env['medical.lab']
        res = medical_lab_obj.create({'name': browse_record.name,
                                   'patient_id': browse_record.patient_id.id,
                                   'date_requested':browse_record.date,
                                   'medical_test_type_id':browse_record.name.id,
                                   'requestor_physician_id': browse_record.doctor_id.id,
                                   })
        res_ids.append(res.id)
        if res_ids:                     
            imd = self.env['ir.model.data']
            action = imd.xmlid_to_object('bi_veterinary_management.action_view_lab_results_tree')
            list_view_id = imd.xmlid_to_res_id('bi_veterinary_management.view_medical_lab')
            form_view_id  =  imd.xmlid_to_res_id('bi_veterinary_management.view_medical_lab_form')

            result = {
                            'name': action.name,
                            'help': action.help,
                            'type': action.type,
                            'views': [[list_view_id,'tree' ],[form_view_id,'form']],
                            'target': action.target,
                            'context': action.context,
                            'res_model': action.res_model,
                            'res_id':res.id,
                        }
        if res_ids:
                result['domain'] = "[('id','=',%s)]" % res_ids

        return result


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    