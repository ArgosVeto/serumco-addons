# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ApiInformationWizard(models.TransientModel):
    _name = 'api.information.wizard'
    _description = 'Wizard to display sale order information Api(centravet) > Odoo'

    description = fields.Text(readonly=True)
    date_sent = fields.Datetime(readonly=True)
    date_integrated = fields.Date(readonly=True)
    date_prepared = fields.Date(readonly=True)
    date_delivered = fields.Date(readonly=True)
    date_billed = fields.Date(readonly=True)
