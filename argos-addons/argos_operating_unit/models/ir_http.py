# -*- coding: utf-8 -*-

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        user = request.env.user
        res = super(IrHttp, self).session_info()
        if request.session.uid:
            user_operating_units = {}
            user_operating_unit_ids = {}
            for company in user.company_ids:
                operation_unit_ids = user.operating_unit_ids.filtered(lambda l: l.company_id.id == company.id)
                user_operating_units[company.id] = [(ou.id, ou.name) for ou in operation_unit_ids]
                user_operating_unit_ids[company.id] = [ou.id for ou in operation_unit_ids]
            res['operating_unit_id'] = user.default_operating_unit_id.id if user.default_operating_unit_id else False
            res['user_operating_units'] = user_operating_units
            res['user_operating_unit_ids'] = user_operating_unit_ids
            res['display_switch_company_menu'] = (user.has_group('base.group_multi_company') and len(
                user.company_ids) > 1) | len(operation_unit_ids) > 1
        return res
