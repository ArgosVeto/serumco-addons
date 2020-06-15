# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime,timedelta

class appointment_start_end_wizard(models.TransientModel):
    _name = "appointment.start.end.wizard"

    physician_ids = fields.Many2many('medical.physician',string='Name Of Physician')
    start_date = fields.Date("Start Date")
    end_date = fields.Date('End Date')
    speciality_ids = fields.Many2many('medical.speciality',string='Speciality')

    def show_record(self):
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        
        result = mod_obj.get_object_reference('bi_veterinary_management','bi_action_medical_appointment')
        id = result and result[1] or False
        if id:
            current_action = act_obj.browse(id)
            result = current_action.read()[0]
            
            domain = []        
            if self.start_date:
                from_date = self.start_date
                from_date = from_date
                domain.append(('appointment_start_date','>=',from_date))
                
            if self.end_date:
                to_date = self.end_date
                to_date = to_date+timedelta(days=1)
                to_date = to_date
                domain.append(('appointment_end_date','<',to_date))
            
            if self.physician_ids:
                domain.append(('doctor_id','in',map(int,self.physician_ids)))
            if self.speciality_ids:
                domain.append(('speciality_id','in',map(int,self.speciality_ids)))
            
            result['domain'] = domain
            result['binding_view_types'] = 'form'
            
            return result
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: