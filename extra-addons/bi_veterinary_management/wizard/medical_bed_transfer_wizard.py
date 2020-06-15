# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date

class medical_bed_transfer_wizard(models.TransientModel):
    _name = "medical.bed.transfer.wizard"
    _recname = 'newbed_id'

    newbed_id = fields.Many2one('medical.hospital.bed',string="New Bed",required=True  )
    reason = fields.Char('Reason',required=True)

    def bed_transfer(self):
        record = self and self[0]
        medic_imp_obj = self.env['medical.inpatient.registration']
        medic_imp_rec= medic_imp_obj.browse(self._context.get('active_id'))
        if medic_imp_rec.state == 'hospitalized':
            if record.newbed_id.state == 'free':
               record.newbed_id.state = 'occuiped'
               medic_imp_rec.write({
                                    'bed_id':record.newbed_id.id,
                                    'bed_transfers_ids': [(0,0,{'date': date.today(),
                                    'bed_to':record.newbed_id.id,
                                    'bed_from':medic_imp_rec.bed_id.id,
                                    'inpatient_id':medic_imp_rec.patient_id.id,
                                    'reason':record.reason})]
                                })
               medic_imp_rec.bed_id = record.newbed_id.id
            else:
                raise UserError("Bed is occupied")
        else:
           raise UserError("Bed transfer is only allowed in hospitalize stage")



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: