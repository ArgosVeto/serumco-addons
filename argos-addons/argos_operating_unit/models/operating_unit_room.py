# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class OperatingUnitRoom(models.Model):
    _name = 'operating.unit.room'
    _description = 'Operating Unit Room'

    name = fields.Char('Name')
    operating_unit_id = fields.Many2one('operating.unit', 'Clinic')
    area = fields.Float('Area (decimal number in m²)')

    @api.constrains('area')
    def _check_area(self):
        if not self._context.get('from_room', False) and not self._context.get('from_bo', False):
            return
        for rec in self:
            if not (0.0 <= rec.area < 1000.0):
                raise ValidationError(_('Room area must be less than 1000m².'))
