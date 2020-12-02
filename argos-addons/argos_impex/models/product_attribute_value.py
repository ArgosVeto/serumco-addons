# -*- coding: utf-8 -*-

from odoo import models, api


# class ProductAttributeValue(models.Model):
#     _inherit = 'product.attribute.value'
#
#     @api.model
#     def manage_attribute_values(self, values=False, attribute=False, logger=False, errors=[]):
#         """
#         Get attribute value
#         :param name:
#         :return:
#         """
#         if not values or not attribute:
#             return False
#         attribute_values = self.env['product.attribute.value']
#         for item in values:
#             try:
#                 value = self.search([('name', '=', item[3]), ('attribute_id', '=', attribute.id)], limit=1)
#                 if not value:
#                     value = self.create({'name':  item[3], 'attribute_id': attribute.id})
#                 attribute_values |= value
#                 self._cr.commit()
#             except Exception as e:
#                 logger.error(repr(e))
#                 errors.append((item, repr(e)))
#                 self._cr.rollback()
#         return attribute_values

