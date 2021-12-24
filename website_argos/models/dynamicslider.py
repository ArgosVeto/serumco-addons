# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models
from odoo.addons.website_sale.controllers import main


class ProductPerPageCountBizople(models.Model):
    _name = "product.per.page.count.bizople"
    _order = 'name asc'
    _description = "Add page no"

    name = fields.Integer(string='Product per page')
    default_active_count = fields.Boolean(string="Set default")
    prod_page_id = fields.Many2one('product.per.page.bizople')

    @api.model
    def create(self, vals):
        res = super(ProductPerPageCountBizople, self).create(vals)
        if vals.get('name') == 0:
            raise Warning(
                _("Warning! You cannot set 'zero' for product page."))
        if vals.get('default_active_count'):
            true_records = self.search(
                [('default_active_count', '=', True), ('id', '!=', res.id)])
            true_records.write({'default_active_count': False})
        return res

    def write(self, vals):
        res = super(ProductPerPageCountBizople, self).write(vals)
        if vals.get('name') == 0:
            raise Warning(
                _("Warning! You cannot set 'zero' for product page."))
        if vals.get('default_active_count'):
            true_records = self.search(
                [('default_active_count', '=', True), ('id', '!=', self.id)])
            true_records.write({'default_active_count': False})
        return res

class ProductPerPageBizople(models.Model):
    _name = "product.per.page.bizople"
    _description = "Add no of product display in one page"

    name = fields.Char(string="Label Name", translate=True)
    prod_count_ids = fields.One2many(
        'product.per.page.count.bizople', 'prod_page_id', string="No of product to display")

    def write(self, vals):
        res = super(ProductPerPageBizople, self).write(vals)
        default_pg = self.env['product.per.page.count.bizople'].search(
            [('default_active_count', '=', True)])
        if default_pg.name:
            main.PPG = int(default_pg.name)
        else:
            raise Warning(
                _("Warning! You have to set atleast one default value."))
        return res

class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    def get_product_category_count(self):
        for obj in self:
            categ_ids = [obj.id]
            sub_ids = [obj.id]
            while sub_ids:
                sub_ids = obj.env['product.public.category'].sudo().search([('parent_id', 'in', sub_ids)]).ids
                categ_ids = categ_ids + sub_ids
            domain = [('public_categ_ids', 'in', list(set(categ_ids)))]
            if not obj.env.user.has_group('base.group_system'):
                domain.append(("website_published", '=', True))
            ctx = obj.env.context or {}
            if 'product_categ_search' in ctx and ctx['product_categ_search']:
                domain.append(("name", 'ilike', ctx['product_categ_search'].strip()))
            product_template = self.env['product.template'].search(domain)
            obj.product_tmpl_count = len(product_template.ids)

    product_tmpl_count = fields.Integer(string="Total Product", compute="get_product_category_count")
    auto_assign = fields.Boolean("Auto Assign")
    quick_categ = fields.Boolean("Quick Category for Mobile", help='Categories visible on mobile view for Quick Search')


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist' 

    auto_assign = fields.Boolean("Auto Assign Category")

class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"
    
    @api.model
    def add_auto_product_category(self):
        category_ids = self.env['product.public.category'].search([('auto_assign', '=', True)]).ids
        for obj in self:
            if obj.product_id:
                ecom_category_ids = obj.product_id.public_categ_ids.ids
                ecom_category_ids = list(set(ecom_category_ids + category_ids))
                obj.product_id.public_categ_ids = [[6, 0, ecom_category_ids]]
            elif obj.product_tmpl_id:
                ecom_category_ids = obj.product_tmpl_id.public_categ_ids.ids
                ecom_category_ids = list(set(ecom_category_ids + category_ids))
                obj.product_tmpl_id.public_categ_ids = [[6, 0, ecom_category_ids]]
            elif obj.categ_id:
                product_ids = self.env['product.product'].search([('categ_id', '=', obj.categ_id.id)])
                for product_id in product_ids:
                    ecom_category_ids = product_id.public_categ_ids.ids
                    ecom_category_ids = list(set(ecom_category_ids + category_ids))
                    product_id.public_categ_ids = [[6, 0, ecom_category_ids]]
            elif obj.applied_on == '3_global':
                product_ids = self.env['product.product'].search([])
                for product_id in product_ids:
                    ecom_category_ids = product_id.public_categ_ids.ids
                    ecom_category_ids = list(set(ecom_category_ids + category_ids))
                    product_id.public_categ_ids = [[6, 0, ecom_category_ids]]
    
    @api.model
    def delete_auto_product_category(self):
        category_ids = self.env['product.public.category'].search([('auto_assign', '=', True)]).ids
        for obj in self:
            if obj.product_id:
                ecom_category_ids = obj.product_id.public_categ_ids.ids
                ecom_category_ids = [categ_id for categ_id in ecom_category_ids if categ_id not in category_ids]
                obj.product_id.sudo().public_categ_ids = [[6, 0, ecom_category_ids]]
            elif obj.product_tmpl_id:
                ecom_category_ids = obj.product_tmpl_id.public_categ_ids.ids
                ecom_category_ids = [categ_id for categ_id in ecom_category_ids if categ_id not in category_ids]
                obj.product_tmpl_id.sudo().public_categ_ids = [[6, 0, ecom_category_ids]]
            elif obj.categ_id:
                product_ids = self.env['product.product'].search([('categ_id', '=', obj.categ_id.id)])
                for product_id in product_ids:
                    ecom_category_ids = product_id.public_categ_ids.ids
                    ecom_category_ids = [categ_id for categ_id in ecom_category_ids if categ_id not in category_ids]
                    product_id.sudo().public_categ_ids = [[6, 0, ecom_category_ids]]
            elif obj.applied_on == '3_global':
                product_ids = self.env['product.product'].search([])
                for product_id in product_ids:
                    ecom_category_ids = product_id.public_categ_ids.ids
                    ecom_category_ids = [categ_id for categ_id in ecom_category_ids if categ_id not in category_ids]
                    product_id.sudo().public_categ_ids = [[6, 0, ecom_category_ids]]
    
    @api.model
    def get_update_category(self, pricelist_id):
        pricelist = False
        if pricelist_id:
            pricelist = self.env['product.pricelist'].browse(pricelist_id)
        for obj in self:
            if not pricelist_id and obj.product_id.pricelist_id:
                pricelist = obj.product_id.pricelist_id
            elif not pricelist_id and obj.product_tmpl_id.pricelist_id:
                pricelist = obj.product_tmpl_id.pricelist_id
            if pricelist:
                if pricelist.auto_assign:
                    obj.add_auto_product_category()
                else:
                    obj.delete_auto_product_category()
    
    @api.model
    def create(self, vals):
        res = super(ProductPricelistItem, self).create(vals)
        if 'pricelist_id' in vals and vals['pricelist_id']:
            res.get_update_category(vals['pricelist_id'])
        return res

    def write(self, vals):
        res = super(ProductPricelistItem, self).write(vals)
        if 'pricelist_id' in vals:
            for obj in self:
                obj.get_update_category(vals['pricelist_id'])
        elif 'product_id' in self:
            for obj in self:
                obj.get_update_category(obj.pricelist_id.id)
        elif 'product_tmpl_id' in vals:
            for obj in self:
                obj.get_update_category(obj.pricelist_id.id)
        return res

    @api.model
    def unlink(self):
        self.delete_auto_product_category()
        return super(ProductPricelistItem, self).unlink()

class BizProductSlider(models.Model):
    _name = 'biz.product.slider'
    _description = 'Product Slider For Website'

    name = fields.Char(string="Slider name", default='Best Seller', required=True,
                       translate=True)
    auto_slide = fields.Boolean(string='Auto Slide', default=True)
    sliding_speed = fields.Integer(string="Sliding speed", default='3000')
    product_ids = fields.Many2many('product.template',
                                            'website_argos_product_template_slider_rel',
                                            'slider_id', 'prod_id',
                                            string="Products")

    active = fields.Boolean(string="Publish on Website", default=True)
    no_of_objects = fields.Selection([('2', '2'), ('3', '3'), ('4', '4'),
                                     ('5', '5'), ('6', '6')], string="Number of Product in one slide",
                                    default='4', required=True)


class BizBrandSlider(models.Model):
    _name = 'biz.brand.slider'
    _description = 'Brand Slider For Website'

    def _get_domain(self):
        filter_id = self.env['product.filter'].search([('name', '=', 'Gamme')]).id
        return [('product_filter_id','=', filter_id)]

    name = fields.Char(string="Slider name", default='Best Brand', required=True,
                       translate=True)
    auto_slide = fields.Boolean(string='Auto Slide', default=True)
    sliding_speed = fields.Integer(string="Sliding speed", default='3000')
    active = fields.Boolean(string="Publish on Website", default=True)
    brand_ids = fields.Many2many('product.filter.line',
                                'website_argos_product_filter_line_slider_rel',
                                'slider_id', 'brand_id',
                                domain=lambda self: self._get_domain(),
                                string="Brands")
    no_of_objects = fields.Selection([('2', '2'), ('3', '3'), ('4', '4'),
                                     ('5', '5'), ('6', '6')], string="Number of Brand in one slide",
                                    default='4', required=True)

class BizMultiTabProductSlider(models.Model):
    _name = 'multi.tab.product.slider'
    _description = "Multi Tab Product Slider"

    name = fields.Char(string="Product Slider Name", default='Featured Products',
                       required=True, translate=True,
                       help="Product Slider Name")
    active = fields.Boolean(string="Active", default=True)

    auto_slide = fields.Boolean(string='Auto Rotate Slider', default=True)
    sliding_speed = fields.Integer(string="Product sliding speed", default='6000',
                                   help='Product sliding speed')
    no_of_tabs = fields.Selection([('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                        string="No. of Tabs", default='2',
                                        required=True,
                                        help="No of Tabs for Product Slider")

    tab_label_1 = fields.Char(string="1st Product Tab", default='First Tab',
                                     required=True, translate=True)
    tab_one_product_ids = fields.Many2many('product.template', 'product_slider_collection_1_rel', 'slider_id',
                                        'prod_id',
                                        required=True, string="1st Product Tab Data", domain="[('is_published', '=', True)]")

    tab_label_2 = fields.Char(string="2nd Product Tab", default='Second Tab',
                                     required=True, translate=True)
    tab_two_product_ids = fields.Many2many('product.template', 'product_slider_collection_2_rel', 'slider_id',
                                        'prod_id', string="2nd Product Tab Data", 
                                        required=True, domain="[('is_published', '=', True)]")

    tab_label_3 = fields.Char(string="3rd Product Tab", default='Third Tab', translate=True)
    tab_three_product_ids = fields.Many2many('product.template', 'product_slider_collection_3_rel', 'slider_id',
                                        'prod_id', domain="[('is_published', '=', True)]",string="3rd Product Tab Data")

    tab_label_4 = fields.Char(string="4th Product Tab", default='Fourth Tab', translate=True)
    tab_four_product_ids = fields.Many2many('product.template', 'product_slider_collection_4_rel', 'slider_id',
                                        'prod_id', domain="[('is_published', '=', True)]", string="4th Product Tab Data")

    tab_label_5 = fields.Char(string="5th Product Tab", default='Fifth collection', translate=True)
    tab_five_product_ids = fields.Many2many('product.template', 'product_slider_collection_5_rel', 'slider_id',
                                        'prod_id',domain="[('is_published', '=', True)]", string="5th Product Tab Data")



class BizBlogSlider(models.Model):
    _name = 'biz.blog.slider'
    _description = 'Blog Slider'

    name = fields.Char(string="Slider name", default='Blogs',
                       required=True, translate=True)
    active = fields.Boolean(string="Publish on Website", default=True)
    blog_subtitle = fields.Text(string="Slider sub title", default='Blog Sub Title',
                            help="""Slider sub title to be display""", translate=True)
    no_of_objects = fields.Selection([('1', '1'), ('2', '2'), ('3', '3')], string="Blogs Count",
                                    default='3',required=True)
    auto_slide = fields.Boolean(string='Auto Rotate Slider', default=True)
    sliding_speed = fields.Integer(string="Slider sliding speed", default='5000')
    blog_post_ids = fields.Many2many('blog.post', 'blogpost_slider_rel', 'slider_id',
                                             'post_id',
                                             string="Blogs", required=True, domain="[('is_published', '=', True)]")


class BizCategorySlider(models.Model):
    _name = 'biz.category.slider'
    _description = 'Category Slider for Website'

    name = fields.Char(string="Slider name", required=True,
                       translate=True,
                       help="""Slider title to be displayed on website
                        like Best Categories, Latest and etc...""")
    active = fields.Boolean(string="Publish on Website", default=True)

    category_ids = fields.Many2many('product.public.category',
                                            's_bizople_theme_category_slider_rel',
                                            'slider_id', 'cat_id',
                                            string="Collections of category")

