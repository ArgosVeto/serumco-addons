from odoo import fields, models, api


class ResPartnerParameter(models.Model):
    _name = 'res.partner.parameter'
    _description = 'Partner Parameter'

    name = fields.Char(required=True)
    gmvet_id = fields.Char('Gmvet Id', required=False)
    type = fields.Selection([('robe', 'Robe'), ('race', 'Race'), ('diet', 'Diet'), ('insurance', 'Insurance'),
                             ('living', 'Living Environment'), ('connection', 'Connection Origin'), ('gender', 'Gender'),
                             ('chip', 'Chip Location'), ('tattoo', 'Tattoo location')], required=True)

    @api.model
    def _get_parameter_by_name(self, name, type):
        parameter = self.search([('name', '=', name), ('type', '=', type)], limit=1)
        if not parameter:
            return self.create({'name': name, 'type': type})
        return parameter

