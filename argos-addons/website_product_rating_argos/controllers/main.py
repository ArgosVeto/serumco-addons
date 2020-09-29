from odoo.http import request
from odoo import fields, http, _
from odoo.addons.website_sale.controllers.main import WebsiteSale
import json

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

