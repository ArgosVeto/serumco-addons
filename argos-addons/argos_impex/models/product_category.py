# -*- coding: utf-8 -*-

from odoo import models, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    @api.model
    def _get_category_by_name(self, name=False):
        """
        Get category by name
        :param name:
        :return:
        """
        if not name:
            return False

        category = self.search([('name', '=', name)], limit=1)
        if not category:
            category = self.create({'name': name})

        return category
