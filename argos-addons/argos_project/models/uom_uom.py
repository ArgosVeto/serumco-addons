# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.osv import expression


class UomUom(models.Model):
    _inherit = 'uom.uom'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('filter_by_product_category', False):
            product = self.env['product.product'].browse(self._context['filter_by_product_category'])
            args = expression.AND([[('category_id', '=', product.uom_id.category_id.id)], list(args)])
        return super(UomUom, self)._search(args, offset=offset, limit=limit, order=order,
                                                count=count, access_rights_uid=access_rights_uid)