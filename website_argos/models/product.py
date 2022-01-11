# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo import models, fields

class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"
    
    attribute_image = fields.Binary("Image")

class ProductFilterLine(models.Model):
    _inherit = "product.filter.line"

    filter_image = fields.Binary("Image")



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tag_ids = fields.Many2many("product.tag",string="Tag")
    tab_ids = fields.Many2many('product.tab','product_tab_table','tab_ids','product_ids',string="Tab")

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False,
                              only_template=False):
        res = super(ProductTemplate, self)._get_combination_info(combination, product_id, add_qty, pricelist, parent_combination,
                                                                 only_template)
        res['price_total'] = res['price'] * add_qty
        return res


class ProductCategoryTemplate(models.Model):
    _inherit = 'product.public.category'

    description =fields.Char(string="Description")
    web_visible = fields.Boolean(string="Visible sur le site")

class ProductTag(models.Model):
    _name = "product.tag"
    _description = "Product Tag"


    name = fields.Char("Name")
    sequence = fields.Integer("Sequence")

class ProductTab(models.Model):
    _name = 'product.tab'
    _description = 'Product Tab'
    _rec_name = 'name'

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence", default=1)
    content = fields.Html(string="Content")
    product_ids = fields.Many2many('product.template','product_tab_table','product_ids','tab_ids', string="product")