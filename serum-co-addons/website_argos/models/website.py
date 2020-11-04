# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models
from odoo.http import request
import base64
from odoo.addons.http_routing.models.ir_http import slug


class res_config(models.TransientModel):
    _inherit = "res.config.settings"

    is_infinite_load = fields.Boolean(string='Infinite Load', related='website_id.is_infinite_load', readonly=False)
    infinite_load_image = fields.Binary(string='Infinite Load Image', related='website_id.infinite_load_image', readonly=False)

    
class BlogPost(models.Model):
    _inherit = "blog.post"

    employee_id = fields.Many2one('hr.employee',string='Employee')

    
class Website(models.Model):
    _inherit = "website"

    @api.model
    def get_consultation_type(self):
        consultation_type_ids = request.env['consultation.type'].sudo().search([])
        return consultation_type_ids

    @api.model
    def get_footer_operating_unit(self):
        operating_unit_ids = request.env['operating.unit'].sudo().search([('show_in_footer','=',True)])
        return operating_unit_ids
    
    @api.model
    def get_clinic(self):
        clinic_ids = request.env['operating.unit'].sudo().search([])
        return clinic_ids

    @api.model
    def operating_unit_services(self):
        service_ids = request.env['operating.unit.service'].sudo().search([],limit=6)
        return service_ids

    @api.model
    def default_category(self,c):
        Category = request.env['product.public.category']
        dom = request.env['website'].get_current_website().website_domain()
        category_id = Category.search(dom,limit=1)
        category_url = '/shop/?search=&attrib=&attrib=%s-%s' %(c.attribute_id.id,c.id)
        return category_url

    @api.model
    def default_category_tmp(self,c):
        category_url = '/shop/?search=&attrib=&attrib=%s-%s' %(c.attribute_id.id,c.product_attribute_value_id.id)
        return category_url

    @api.model
    def get_gamne_values(self):
        gamne_values = request.env['product.attribute'].sudo().search([('name','=','Gamme')],limit=5)
        att_value = False
        if gamne_values:
            att_value = gamne_values[0].value_ids
        return att_value

    @api.model
    def get_product_gamne_values(self,product):
        att_value = False
        att_list = []
        if product.attribute_line_ids:
            for line in product.attribute_line_ids:
                if line.attribute_id.name == 'Gamme':
                    att_list = line.value_ids                    
        return att_list

        

    @api.model
    def get_cash_values(self):
        cash_values = request.env['product.attribute'].sudo().search([('name','=','Espèces')])
        att_value = False
        if cash_values:
            att_value = cash_values[0].value_ids
        return att_value

    @api.model
    def get_categories(self):
        category_ids = self.env['product.public.category'].search(
            [('parent_id', '=', False)])
        res = {
            'categories': category_ids,
        }
        return res
    
    @api.model
    def get_product_category_data_menu(self):
        category_ids = self.env['product.public.category'].sudo().search([('quick_categ', '=', True)])
        return category_ids
    
    @api.model
    def get_auto_assign_category(self):
        auto_assign_categ_ids = self.env['product.public.category'].search([('auto_assign','=',True)])
        return auto_assign_categ_ids


    def add_fav_clinic(self,operating_unit):
        partner_id =  self.env.user.partner_id
        if partner_id.clinic_shortlisted_ids.ids:
            check_operating_uni = any(operating_unit.id == cs.favorite_clinic_id.id for cs in partner_id.clinic_shortlisted_ids)
            if not check_operating_uni:
                for cs in partner_id.clinic_shortlisted_ids:
                    cs.unlink()
                partner_id.clinic_shortlisted_ids = [(0,0,{'favorite_clinic_id':operating_unit.id})]
            else:
                for cs in partner_id.clinic_shortlisted_ids:
                    cs.unlink()
        else:
            partner_id.clinic_shortlisted_ids = [(0,0,{'favorite_clinic_id':operating_unit.id})]
        return operating_unit


    def get_product_brands(self, category, **post):
        domain = []
        if category:
            cat_id = []
            if category != None:
                for ids in category:
                    cat_id.append(ids.id)
                domain += ['|', ('public_categ_ids.id', 'in', cat_id),
                           ('public_categ_ids.parent_id', 'in', cat_id)]
        else:
            domain = []
        product_ids = self.env["product.template"].sudo().search(domain)
        domain_brand = [
            ('product_ids', 'in', product_ids.ids or []), ('product_ids', '!=', False)]
        brands = self.env['product.brand'].sudo().search(domain_brand)
        return brands
    
    def get_product_count_argos(self):
        prod_per_page = self.env['product.per.page.bizople'].search([])
        prod_per_page_no = self.env['product.per.page.count.bizople'].search([])
        values = {'name': prod_per_page.name,
            'page_no': prod_per_page_no,
        }
        return values

    def get_current_pager_selection(self):
        page_no = request.env['product.per.page.count.bizople'].sudo().search(
            [('default_active_count', '=', True)])
        if request.session.get('default_paging_no'):
            return int(request.session.get('default_paging_no'))
        elif page_no:
            return int(page_no.name)

    def get_mailing_list(self):
        mailing_list_ids = self.env['mailing.list'].sudo().search([])
        return mailing_list_ids
        
    is_infinite_load = fields.Boolean(string='Infinite Load', default=True,readonly=False)
    infinite_load_image = fields.Binary('Infinite Load Image', readonly=False)
