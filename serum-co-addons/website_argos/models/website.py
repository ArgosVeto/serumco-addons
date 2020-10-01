# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models
from odoo.http import request
import base64


class res_config(models.TransientModel):
    _inherit = "res.config.settings"

    is_infinite_load = fields.Boolean(string='Infinite Load', related='website_id.is_infinite_load', readonly=False)
    infinite_load_image = fields.Binary(string='Infinite Load Image', related='website_id.infinite_load_image', readonly=False)

    
class Website(models.Model):
    _inherit = "website"

    @api.model
    def get_consultation_type(self):
        consultation_type_ids = request.env['consultation.type'].sudo().search([])
        return consultation_type_ids

#     @api.model
#     def get_footer_operating_unit(self):
#         operating_unit_ids = request.env['operating.unit'].sudo().search([('show_in_footer','=',True)])
#         return operating_unit_ids
    
    @api.model
    def get_clinic(self):
        clinic_ids = request.env['operating.unit'].sudo().search([])
        return clinic_ids

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
                partner_id.clinic_shortlisted_ids = [(0,0,{'favorite_clinic_id':operating_unit.id})]
            else:
                for cs in partner_id.clinic_shortlisted_ids:
                    if(operating_unit.id == cs.favorite_clinic_id.id):
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
