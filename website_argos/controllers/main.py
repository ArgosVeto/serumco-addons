    # -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

import re
import math
import json
import os
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo import http, SUPERUSER_ID, fields
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website_sale.controllers import main
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.sale.controllers.variant import VariantController
from odoo.osv import expression

class PortalUser(http.Controller):
    @http.route(['/update-image'], type='json', auth="user")
    def action_update_image(self,**post):
        datas_file = str(post['img_attachment']).split(',')
        datas_file = datas_file[1]
        user_id = request.env.user
        datas_file = ''
        if 'img_attachment' in post and post['img_attachment']:
            datas_file = str(post['img_attachment']).split(',')
            datas_file = datas_file[1]
            user_id.write({'image_1920':datas_file})
        values = {'user_id':user_id}
        return request.env['ir.ui.view'].render_template("website_argos.update_user_image",values)
        
class WebsiteCategoyBizople(http.Controller):
    _per_page_category = 20
    _per_page_brand = 20
   
    @http.route([
        '/category',
        '/category/page/<int:page>',
        '/category/<model("product.public.category"):category_id>',
        '/category/<model("product.public.category"):category_id>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def product_category_data(self, page=1, category_id=None, search='', **post):
        if search:
            categories = [categ for categ in request.env['product.public.category'].search([
                ('name', 'ilike', search)]
            )]
        else:
            if category_id:
                categories = [categ for categ in request.env['product.public.category'].search([
                    ('parent_id', '=', category_id.id)]
                )]
            else:
                categories = [categ for categ in request.env['product.public.category'].search([
                    ('parent_id', '=', False)]
                )]
        if not categories and category_id:
            url = "/shop/category/%s" % slug(category_id)
            return request.redirect(url)
        else:
            pager = request.website.pager(
                url=request.httprequest.path.partition('/page/')[0],
                total=len(categories),
                page=page,
                step=self._per_page_category,
                url_args=post,
            )
            pager_begin = (page - 1) * self._per_page_category
            pager_end = page * self._per_page_category
            categories = categories[pager_begin:pager_end]
            return request.render('website_argos.website_sale_categoy_list_bizople', {
                'categories': categories,
                'pager': pager,
                'search': search
            })

    @http.route([
        '/category-search',
    ], type='http', auth="public", website=True)
    def product_category_search_data(self, **post):
        return request.redirect('/category?&search=%s' % post['search'])

#    @http.route([
#        '/brand',
#        '/brand/page/<int:page>',
#        '/brand/<model("product.brand"):brand_id>',
#        '/brand/<model("product.brand"):brand_id>/page/<int:page>'
#    ], type='http', auth="public", website=True)
#    def product_brand_data(self, page=1, brand_id=None, search='', **post):
#        if search:
#            brands = [brand for brand in request.env['product.brand'].search([
#                ('name', 'ilike', search)]
#            )]
#        else:
#            if brand_id:
#                brands = [brand for brand in request.env['product.brand'].search([
#                    ('parent_id', '=', brand_id.id)]
#                )]
#            else:
#                brands = [brand for brand in request.env['product.brand'].search([
#                    ('parent_id', '=', False)]
#                )]
#        if not brands and brand_id:
#            url = "/shop?brand=%s" % slug(brand_id)
#            return request.redirect(url)
#        else:
#            pager = request.website.pager(
#                url=request.httprequest.path.partition('/page/')[0],
#                total=len(brands),
#                page=page,
#                step=self._per_page_brand,
#                url_args=post,
#            )
#            pager_begin = (page - 1) * self._per_page_brand
#            pager_end = page * self._per_page_brand
#            brands = brands[pager_begin:pager_end]
#            return request.render('website_argos.website_sale_brand_list_bizople', {
#                'brands': brands,
#                'pager': pager,
#                'search': search
#            })

#    @http.route([
#        '/brand-search',
#    ], type='http', auth="public", website=True)
#    def brand_search_data(self, **post):
#        return request.redirect('/brand?&search=%s' % post['search'])


class BizopleWebsiteSale(WebsiteSale):

    @http.route('/get_prod_quick_view_details', type='json', auth='public', website=True)
    def get_product_qv_details(self, **kw):
        product_id = int(kw.get('prod_id', 0))
        if product_id > 0:
            product = http.request.env['product.template'].search([('id', '=', product_id)])
            pricelist = request.website.get_current_pricelist()
            from_currency = request.env.user.company_id.currency_id
            to_currency = pricelist.currency_id
            compute_currency = lambda price: from_currency.compute(price, to_currency)
            
            return request.env['ir.ui.view'].render_template("website_argos.get_product_qv_details_template", 
                   {'product': product, 'compute_currency': compute_currency or None,})
            
        else:
            
            return request.env['ir.ui.view'].render_template("website_argos.get_product_qv_details_template", 
                   {'error': _('some problem occurred product no loaded properly')})


    @http.route(['/shop/pager_selection/<model("product.per.page.count.bizople"):pl_id>'], type='http', auth="public", website=True)
    def product_page_change(self, pl_id, **post):
        request.session['default_paging_no'] = pl_id.name
        main.PPG = pl_id.name
        return request.redirect(request.httprequest.referrer or '/shop')

    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>''',
        '''/shop/brands'''
    ], type='http', auth="public", website=True, sitemap=WebsiteSale.sitemap_shop)
    def shop(self, page=0, category=None, search='', ppg=False, brands=None, **post):
        if request.env['website'].sudo().get_current_website().theme_id.name == 'theme_argos':
            add_qty = int(post.get('add_qty', 1))
            Category = request.env['product.public.category']
            if category:
                category = Category.search(
                    [('id', '=', int(category))], limit=1)
                if not category or not category.can_access_from_current_website():
                    raise NotFound()
            else:
                category = Category
            if brands:
                req_ctx = request.context.copy()
                req_ctx.setdefault('brand_id', int(brands))
                request.context = req_ctx
            result = super(BizopleWebsiteSale, self).shop(
                page=page, category=category, search=search, ppg=ppg, **post)
            page_no = request.env['product.per.page.count.bizople'].sudo().search(
                [('default_active_count', '=', True)])
            if page_no:
                ppg = int(page_no.name)
            else:
                ppg = result.qcontext['ppg']

            ppr = request.env['website'].get_current_website().shop_ppr or 4

            attrib_list = request.httprequest.args.getlist('attrib')
            attrib_values = [[int(x) for x in v.split("-")]
                             for v in attrib_list if v]
            attributes_ids = {v[0] for v in attrib_values}
            attrib_set = {v[1] for v in attrib_values}
            request.env.context = dict(request.env.context, with_filter_object=True)
            domain = self._get_search_domain(search, category, attrib_values)
            url = "/shop"
            if search:
                post["search"] = search
            if attrib_list:
                post['attrib'] = attrib_list
            if post:
                request.session.update(post)

            Product = request.env['product.template'].with_context(
                bin_size=True)
            session = request.session
            cate_for_price = None
            search_product = Product.search(domain)
            print(search_product)
            website_domain = request.website.website_domain()
            pricelist_context, pricelist = self._get_pricelist_context()
            categs_domain = [('parent_id', '=', False)] + website_domain
            if search:
                search_categories = Category.search(
                    [('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
                categs_domain.append(('id', 'in', search_categories.ids))
            else:
                search_categories = Category
            categs = Category.search(categs_domain)

            if category:
                url = "/shop/category/%s" % slug(category)
                cate_for_price = int(category)
            prevurl = request.httprequest.referrer
            if prevurl:
                if not re.search('/shop', prevurl, re.IGNORECASE):
                    request.session['pricerange'] = ""
                    request.session['min1'] = ""
                    request.session['max1'] = ""
                    request.session['curr_category'] = ""
            brand_list = request.httprequest.args.getlist('brand')
            brand_list = [unslug(x)[1] for x in brand_list]
            brand_set = set([int(v) for v in brand_list])
            if brand_list:
                brandlistdomain = list(map(int, brand_list))
                domain += [('brand_id', 'in', brandlistdomain)]
                bran = []
                brand_obj = request.env['product.brand'].sudo().search(
                    [('id', 'in', brandlistdomain)])
                if brand_obj:
                    for vals in brand_obj:
                        if vals.name not in bran:
                            bran.append((vals.name, vals.id))
                    if bran:
                        request.session["brand_name"] = bran
            if not brand_list:
                request.session["brand_name"] = ''
            product_count = len(search_product)

            if cate_for_price:
                request.session['curr_category'] = float(cate_for_price)
            if request.session.get('default_paging_no'):
                ppg = int(request.session.get('default_paging_no'))
            keep = QueryURL('/shop', category=category and int(category),
                            search=search, attrib=attrib_list, order=post.get('order'))
            product_count = Product.search_count(domain)
            pager = request.website.pager(
                url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
            products = Product.search(
                domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))

            ProductFilter = request.env['product.filter']
            if products:
                # get all products without limit
                filters = ProductFilter.search(
                    [('product_tmpl_ids', 'in', search_product.ids)])
            else:
                filters = ProductFilter.browse(attributes_ids)

            layout_mode = request.session.get('website_sale_shop_layout_mode')
            if not layout_mode:
                if request.website.viewref('website_sale.products_list_view').active:
                    layout_mode = 'list'
                else:
                    layout_mode = 'grid'
            active_brand_list = list(set(brand_set))

            if search:
                domain.append(("name", 'ilike', search.strip()))
            if not request.env.user.has_group('base.group_system'):
                    domain.append(("website_published", '=', True))
            product_tmpl_ids = request.env['product.template'].search(domain).ids
            result.qcontext.update({
                'search': search,
                'total_product_count': len(product_tmpl_ids),
                'category': category,
                'attrib_values': attrib_values,
                'attrib_set': attrib_set,
                'pager': pager,
                'filters': filters,
                'add_qty': add_qty,
                'products': products,
                'search_count': product_count,  # common for all searchbox
                'bins': TableCompute().process(products, ppg, ppr),
                'ppg': ppg,
                'ppr': ppr,
                'categories': categs,
                'attributes': attributes,
                'keep': keep,
                'search_categories_ids': search_categories.ids,
                'layout_mode': layout_mode,
                'brand_set': brand_set,
                'active_brand_list': active_brand_list,
            })
            return result
        else:
            return  super(BizopleWebsiteSale, self).shop(page=page, category=category, search=search, ppg=ppg, **post)


class bizcommonSliderSettings(http.Controller):

    def get_blog_data(self, slider_filter):
        slider_header = request.env['biz.blog.slider'].sudo().search(
            [('id', '=', int(slider_filter))])
        values = {
            'slider_header': slider_header,
            'blog_slider_details': slider_header.blog_post_ids,
        }
        return values

    def get_categories_data(self, slider_id):
        slider_header = request.env['biz.category.slider'].sudo().search(
            [('id', '=', int(slider_id))])
        values = {
            'slider_header': slider_header
        }
        values.update({
            'slider_details': slider_header.category_ids,
        })
        return values


    @http.route(['/website_argos/blog_get_options'], type='json', auth="public", website=True)
    def bizcommon_get_slider_options(self):
        slider_options = []
        option = request.env['biz.blog.slider'].search(
            [('active', '=', True)], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options



    @http.route(['/website_argos/second_blog_get_dynamic_slider'], type='http', auth='public', website=True)
    def second_get_dynamic_slider(self, **post):
        if post.get('slider-type'):
            values = self.get_blog_data(post.get('slider-type'))
            return request.render("website_argos.bizcommon_blog_slider_view", values)


    @http.route(['/website_argos/blog_image_effect_config'], type='json', auth='public', website=True)
    def bizcommon_product_image_dynamic_slider(self, **post):
        slider_data = request.env['biz.blog.slider'].search(
            [('id', '=', int(post.get('slider_filter')))])
        values = {
            's_id': str(slider_data.no_of_objects) + '-' + str(slider_data.id),
            'counts': slider_data.no_of_objects,
            'auto_slide': slider_data.auto_slide,
            'auto_play_time': slider_data.sliding_speed,
        }
        return values


    @http.route(['/website_argos/category_get_options'], type='json', auth="public", website=True)
    def category_get_slider_options(self):
        slider_options = []
        option = request.env['biz.category.slider'].search(
            [('active', '=', True)], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options


    @http.route(['/website_argos/category_slider_3'], type='http', auth='public', website=True)
    def category_slider_value(self, **post):
        if post.get('slider-id'):
            values = self.get_categories_data(post.get('slider-id'))
            return request.render("website_argos.s_bizople_theme_category_slider_view", values)

    @http.route(['/website_argos/bizcommon_image_effect_config'], type='json', auth='public', website=True)
    def category_image_dynamic_slider(self, **post):
        slider_data = request.env['biz.category.slider'].search(
            [('id', '=', int(post.get('slider_id')))])
        values = {
            's_id': slider_data.name.lower().replace(' ', '-') + '-' + str(slider_data.id),
            'counts': slider_data.no_of_objects,
            'auto_slide': slider_data.auto_slide,
            'auto_play_time': slider_data.sliding_speed,
        }
        return values

    @http.route(['/website_argos/product_get_options'], type='json', auth="public", website=True)
    def product_get_slider_options(self):
        slider_options = []
        option = request.env['biz.product.slider'].search(
            [('active', '=', True)], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options

    @http.route(['/website_argos/product_get_dynamic_slider'], type='http', auth='public', website=True)
    def product_get_dynamic_slider(self, **post):
        if post.get('slider-id'):
            slider_header = request.env['biz.product.slider'].sudo().search(
                [('id', '=', int(post.get('slider-id')))])
            values = {
                'slider_header': slider_header
            }
            values.update({
                'slider_details': slider_header.product_ids,
            })
            return request.render("website_argos.website_argos_product_slider_view", values)

    @http.route(['/website_argos/slider_product_call'], type='json', auth='public', website=True)
    def product_image_dynamic_slider(self, **post):
        slider_data = request.env['biz.product.slider'].search(
            [('id', '=', int(post.get('slider_id')))])
        values = {
            's_id': (slider_data.name.lower().replace(' ', '-') + '-' + str(slider_data.id)) if slider_data else '',
            'counts': slider_data.no_of_objects,
            'auto_slide': slider_data.auto_slide,
            'auto_play_time': slider_data.sliding_speed,
        }
        return values

    @http.route(['/website_argos/product_multi_get_options'], type='json', auth="public", website=True)
    def product_multi_get_slider_options(self):
        slider_options = []
        option = request.env['multi.tab.product.slider'].sudo().search(
            [('active', '=', True)], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options

    @http.route(['/tabpro/product_multi_get_dynamic_slider'], type='http', auth='public', website=True)
    def ecomm_multi_get_dynamic_slider(self, **post):
        context, pool = dict(request.context), request.env
        if post.get('slider-type'):
            slider_header = request.env['multi.tab.product.slider'].sudo().search(
                [('id', '=', int(post.get('slider-type')))])

            if not context.get('pricelist'):
                pricelist = request.website.get_current_pricelist()
                context = dict(request.context, pricelist=int(pricelist))
            else:
                pricelist = pool.get('product.pricelist').browse(
                    context['pricelist'])

            context.update({'pricelist': pricelist.id})
            from_currency = pool['res.users'].sudo().browse(
                SUPERUSER_ID).company_id.currency_id
            to_currency = pricelist.currency_id

            def compute_currency(price): return pool['res.currency']._convert(
                price, from_currency, to_currency, fields.Date.today())
            values = {
                'slider_details': slider_header,
                'slider_header': slider_header,
                'compute_currency': compute_currency,
            }
            return request.render("website_argos.bizcommon_multi_cat_slider_view", values)


    @http.route(['/website_argos/multi_tab_product_call'], type='json', auth='public', website=True)
    def product_multi_product_image_dynamic_slider(self, **post):
        slider_data = request.env['multi.tab.product.slider'].sudo().search(
            [('id', '=', int(post.get('slider_filter')))])
        values = {
            's_id': slider_data.no_of_tabs + '-' + str(slider_data.id),
            'counts': slider_data.no_of_tabs,
            'auto_slide': slider_data.auto_slide,
            'auto_play_time': slider_data.sliding_speed,
        }
        return values



class CategoryData(http.Controller):
    @http.route([
        '''/category-data''',
        '''/category-data/category/<model("product.public.category"):category>''',
        '''/category-data/<model("product.public.category"):category>''',
        '''/category-data/<model("product.public.category"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True, sitemap='')
    def categorydata(self, page=0, category=None, search='', ppg=False, **post):
        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category
        keep = QueryURL('/category-data', category=category and int(category), search=search, attrib='', order='')
        url = "/category-data"
        if search:
            post["search"] = search

        categs_domain = [('parent_id', '=', False)]

        if search:
            search_categories = Category.search([]).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = Category.search(categs_domain)
        if category:
            url = "/category-data/category/%s" % slug(category)

        values = {
            'search': search,
            'category': category,
            'categories': categs,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
        }
        if category:
            values['main_object'] = category
        return request.render("website_argos.template_products_categories", values)

class WebsiteSale(WebsiteSale):
    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['GET', 'POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        product_tmpl_id = False
        if 'product_tmpl_id' in kw and kw['product_tmpl_id']:
            product_tmpl_id = int(kw['product_tmpl_id'])
        if 'ptal' in kw and kw['ptal']:
            product_variant_ids = False
            if product_tmpl_id:
                cart_product_id = request.env['product.template'].sudo().browse(product_tmpl_id)
                if cart_product_id.product_variant_ids:
                    product_variant_ids = cart_product_id.product_variant_ids.filtered(lambda s:  int(kw['ptal']) in s.product_template_attribute_value_ids.ids)
                if product_variant_ids:
                    product_id = product_variant_ids[0]
                    product_id = product_id.id
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)

        product_custom_attribute_values = None
        if kw.get('product_custom_attribute_values'):
            product_custom_attribute_values = json.loads(kw.get('product_custom_attribute_values'))

        no_variant_attribute_values = None
        if kw.get('no_variant_attribute_values'):
            no_variant_attribute_values = json.loads(kw.get('no_variant_attribute_values'))

        no_variant_attribute_values = None
        if kw.get('ptal'):
            no_variant_attribute_values = json.loads(kw.get('no_variant_attribute_values'))
        sale_order._cart_update(
            product_id=int(product_id),
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values,
        )
        if kw.get('express'):
            return request.redirect("/shop/checkout?express=1")
        return request.redirect("/shop/cart")


    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        res = super(WebsiteSale, self)._get_search_domain(search=search,
                                                          category=category,
                                                          attrib_values=attrib_values,
                                                          search_in_description=search_in_description)
        if request.env.context.get('with_filter_object'):
            domains = [request.website.sale_product_domain()]
            if search:
                for srch in search.split(" "):
                    subdomains = [
                        [('name', 'ilike', srch)],
                        [('product_variant_ids.default_code', 'ilike', srch)]
                    ]
                    if search_in_description:
                        subdomains.append([('description', 'ilike', srch)])
                        subdomains.append([('description_sale', 'ilike', srch)])
                    domains.append(expression.OR(subdomains))

            if category:
                domains.append([('public_categ_ids', 'child_of', int(category))])

            if attrib_values:
                attrib = None
                ids = []
                for value in attrib_values:
                    if not attrib:
                        attrib = value[0]
                        ids.append(value[1])
                    elif value[0] == attrib:
                        ids.append(value[1])
                    else:
                        domains.append([('product_filter_ids.filter_line_ids', 'in', ids)])
                        attrib = value[0]
                        ids = [value[1]]
                if attrib:
                    domains.append([('product_filter_ids.filter_line_ids', 'in', ids)])
            return expression.AND(domains)
        return res


    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True, sitemap=WebsiteSale.sitemap_shop)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = request.env['website'].get_current_website().shop_ppg or 20

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}
        request.env.context = dict(request.env.context, with_filter_object=True)
        domain = self._get_search_domain(search, category, attrib_values)

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))

        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        Product = request.env['product.template'].with_context(bin_size=True)

        search_product = Product.search(domain)
        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search([('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = Category.search(categs_domain)

        if category:
            url = "/shop/category/%s" % slug(category)

        product_count = len(search_product)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        if 'tag_id' in post and post['tag_id']:
            domain.append(('tag_ids','in',[int(post['tag_id'])]))
        products = Product.search(domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))

        ProductFilter = request.env['product.filter']
        if products:
            # get all products without limit
            filters = ProductFilter.search(
                [('product_tmpl_ids', 'in', search_product.ids)])
        else:
            filters = ProductFilter.browse(attributes_ids)
        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if request.website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'
        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg, ppr),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'filters': filters,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
        }
        if category:
            values['main_object'] = category
        return request.render("website_sale.products", values)

class ProductRate(WebsiteSale):

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', order=None, **kwargs):
        product_rating_ids = []
        res = super(ProductRate, self).product(product, category, search)
        if not order:
            order = 'desc'
        if order == 'asc':
            product_rating_ids = request.env['mail.message'].search([('res_id', '=', product.id),('message_type', '=', 'comment')], 
                                                                          order='id asc')
        if order == 'desc':
            product_rating_ids = request.env['mail.message'].search([('res_id', '=', product.id),('message_type', '=', 'comment')], 
                                                                          order='id desc')
        res.qcontext['rating_ids'] = product_rating_ids

        return res

