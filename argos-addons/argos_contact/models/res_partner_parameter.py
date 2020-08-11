from odoo import fields, models, api


class ResPartnerParameter(models.Model):
    _name = 'res.partner.parameter'
    _description = 'Partner Parameter'

    name = fields.Char(required=True)
    gmvet_id = fields.Char('Gmvet Id', required=False)
    type = fields.Selection([('robe', 'Robe'), ('race', 'Race'), ('diet', 'Diet'), ('insurance', 'Insurance'),
                             ('living', 'Living Environment'), ('connection', 'Connection Origin')], required=True)

