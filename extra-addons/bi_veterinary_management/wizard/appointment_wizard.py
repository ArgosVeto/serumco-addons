# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class appointment_wizard(models.TransientModel):
    _name = "appointment.wizard"

    bi_physician_id = fields.Many2one('medical.physician',string="Name Of Physician")
    appointment_date = fields.Date('Appointment Date')
    
    def show_record(self):
        res = {}
        list_of_ids =[]
        appointment_obj = self.env['medical.appointment'].search([('doctor_id','=',self.bi_physician_id.id),('appointment_start_date','=',self.appointment_date)])
        for id in appointment_obj:
            list_of_ids.append(id.id)
        res = self.env['ir.actions.act_window'].for_xml_id('bi_veterinary_management', 'bi_action_medical_appointment')
        res['domain'] = "[('id','in',%s)]" % list_of_ids
        return res
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: