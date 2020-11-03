# -*- coding: utf-8 -*-

import json
import requests
from odoo import http, fields
from odoo.http import request
from werkzeug.exceptions import NotFound
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.payment.controllers.portal import PaymentProcessing


class WebsiteSale(WebsiteSale):

    def _response_status_check(self, code):
        if code == 400:
            ret = 'missing information'
        elif code == 401:
            ret = 'unauthorized'
        elif code == 403:
            ret = 'forbidden'
        elif code == 404:
            ret = 'not found request'
        elif code == 200:
            ret = 'Success'
        else:
            ret = 'not identified'
        return ret

    def _get_auth_token(self, log_res_id=None, log_model_name=None):
        # TODO: Config system parameter: api.centravet.auth.token, api.centravet.stock, api.centravet.login.password
        URL = request.env['ir.config_parameter'].sudo().get_param('api.centravet.auth.token')
        headers = {'Content-Type': 'application/json'}
        mail = request.env['ir.config_parameter'].sudo().get_param('api.centravet.login.mail')
        password = request.env['ir.config_parameter'].sudo().get_param('api.centravet.login.password')
        payload = {'email': mail, 'password': password}

        response = requests.post(url=URL, headers=headers, data=json.dumps(payload))

        reason = self._response_status_check(response.status_code)

        request.env['soap.wsdl.log'].sudo().create({
            'name': 'API stock centravet AUTH',
            'res_id': log_res_id,
            'model_id': request.env['ir.model'].sudo().search([('model', '=', log_model_name)], limit=1).id,
            'msg': "Ask API authorization token",
            'date': fields.Datetime.today(),
            'state': 'successful' if response.status_code == 200 else 'error',
            'reason': reason,
        })

        return response.json() if response.status_code == 200 else False

    def _get_products_availabilities(self, products, token, centravet_code, log_res_id=None, log_model_name=None):
        # TODO: Config system parameter: centravet.subscriber_code api.centravet.stock
        subscriber_code = request.env['ir.config_parameter'].sudo().get_param('centravet.subscriber_code')
        # TODO "str.format est plys pythonic, cette forme de concatenation est obsolete  au python3
        URL = request.env['ir.config_parameter'].sudo().get_param('api.centravet.stock') + '/' + subscriber_code + '?codeClinique=' + \
              centravet_code\
              + \
              '&homeDelivery=false'
        headers = {'Content-Type': 'application/json', 'Authorization': 'bearer ' + token}
        payload = products
        response = requests.post(url=URL, headers=headers, data=json.dumps(payload))

        reason = self._response_status_check(response.status_code)

        request.env['soap.wsdl.log'].sudo().create({
            'name': 'API stock check product availability',
            'res_id': log_res_id,
            'model_id': request.env['ir.model'].sudo().search([('model', '=', log_model_name)], limit=1).id,
            'msg': "Ask API to check if products are available",
            'date': fields.Datetime.today(),
            'state': 'successful' if response.status_code == 200 else 'error',
            'reason': reason,
        })

        return response.json() if (response.status_code == 200) else False

    def check_product_availability(self, product_id, product_qty):
        # TODO: attendre que l'integrateur qui s'occupe du front finisse pour savoir comment avoir accès au clinical_code sans l'obj "order"
        centravet_code = "330704"
        #FIXME: requete inutile de search
        # Equivalent a Select ID Where ID=X.
        # Autant Read direct > request.env['product.product'].browse(product_id.id)
        product_obj = request.env['product.product'].search([('id', '=', product_id)], limit=1)
        if product_obj:
            token = self._get_auth_token(product_obj.id, 'product.product')
            if token:
                # TODO: adapter au TODO précédent
                if not centravet_code:
                    return 'error'
                products = [{'articlecode': product_obj.code, "quantity": product_qty}]
                product_availability = self._get_products_availabilities(products, token, centravet_code, product_obj.id, 'product.product')
                if not product_availability:
                    return 'error'
                return 'yes' if product_availability[0]['available'] else 'no'
        return 'error'

    def check_products_availabilities(self, order):
        if order:
            token = self._get_auth_token(order.id, 'sale.order')
            if token:
                products = []
                for line in order.order_line:
                    if line.product_id.product_tmpl_id.type == 'product' and line.product_id.default_code:
                        products.append({
                            "articlecode": line.product_id.code,
                            "quantity": line.product_uom_qty,
                        })
                if (not order.operating_unit_id) or (not order.operating_unit_id.code):
                    return 'error'
                products_availabilities = self._get_products_availabilities(products, token, order.operating_unit_id.code,
                                                                            order.id, 'sale.order')
                if products_availabilities:
                    unavailable_products = []
                    for availability in products_availabilities:
                        if availability['available'] is False:
                            unavailable_products.append(request.env['product.product'].search([('default_code', '=', availability[
                                'articleCode'])],
                                                                                           limit=1).id)
                    return unavailable_products
        return 'error'

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        res = super(WebsiteSale, self).shop(page, category, search, ppg, **post)
        attributes = res.qcontext.get('attributes', False)
        if attributes:
            res.qcontext.update(attributes=attributes.filtered(lambda attr: attr.is_attribute_visible))
        return res

    @http.route(['/shop/product/check'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def shop_product_check(self, product_id, product_qty):
        return {'status': self.check_product_availability(product_id, product_qty)}

    @http.route(['/shop/cart'], type='http', auth="public", website=True, sitemap=False)
    def cart(self, access_token=None, revive='', unavailable_products=[], **post):
        """
        Main cart management + abandoned cart revival
        access_token: Abandoned cart SO access token
        revive: Revival method when abandoned cart. Can be 'merge' or 'squash'
        """

        order = request.website.sale_get_order()
        if order and order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order()
        values = {}
        if access_token:
            abandoned_order = request.env['sale.order'].sudo().search([('access_token', '=', access_token)], limit=1)
            if not abandoned_order:  # wrong token (or SO has been deleted)
                raise NotFound()
            if abandoned_order.state != 'draft':  # abandoned cart already finished
                values.update({'abandoned_proceed': True})
            elif revive == 'squash' or (revive == 'merge' and not request.session.get('sale_order_id')):
                request.session['sale_order_id'] = abandoned_order.id
                return request.redirect('/shop/cart')
            elif revive == 'merge':
                abandoned_order.order_line.write({'order_id': request.session['sale_order_id']})
                abandoned_order.action_cancel()
            elif abandoned_order.id != request.session.get('sale_order_id'):  # abandoned cart found, user have to choose what to do
                values.update({'access_token': abandoned_order.access_token})

        values.update({
            'website_sale_order': order,
            'date': fields.Date.today(),
            'suggested_products': [],
            'unavailable_products': unavailable_products,
        })

        if order:
            order.order_line.filtered(lambda l: not l.product_id.active).unlink()
            _order = order
            if not request.env.context.get('pricelist'):
                _order = order.with_context(pricelist=order.pricelist_id.id)
            values['suggested_products'] = _order._cart_accessories()

        if post.get('type') == 'popover':
            # force no-cache so IE11 doesn't cache this XHR
            return request.render("website_sale.cart_popover", values, headers={'Cache-Control': 'no-cache'})

        return request.render("website_sale.cart", values)

    @http.route(['/shop/error_service'], type='http', auth="public", website=True, sitemap=False, csrf=False)
    def shop_error_service(self):
        return request.render("argos_website.error_service")

    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        order = request.website.sale_get_order()

        unavailable_products = self.check_products_availabilities(order)
        if unavailable_products and isinstance(unavailable_products, list) and len(unavailable_products):
            return unavailable_products
        elif unavailable_products == 'error':
            return self.shop_error_service()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            return request.redirect('/shop/address')

        for f in self._get_mandatory_billing_fields():
            if not order.partner_id[f]:
                return request.redirect('/shop/address?partner_id=%d' % order.partner_id.id)

        values = self.checkout_values(**post)

        if post.get('express'):
            return request.redirect('/shop/confirm_order')

        values.update({'website_sale_order': order})

        # Avoid useless rendering if called in ajax
        if post.get('xhr'):
            return 'ok'
        return request.render("website_sale.checkout", values)

    @http.route(['/shop/redirect/cart'], auth="public", website=True, sitemap=False, csrf=False)
    def redirect_cart(self, **post):
        unavailable_products = []
        if post:
            size = int(post.get('unavailable_products_length'))
            i = 0
            while(i < size):
                unavailable_products.append(int(post.get('unavailable_product_' + str(i))))
                i += 1
        return self.cart(unavailable_products=unavailable_products)

    @http.route(['/shop/payment/transaction/',
                 '/shop/payment/transaction/<int:so_id>',
                 '/shop/payment/transaction/<int:so_id>/<string:access_token>'], type='json', auth="public", website=True)
    def payment_transaction(self, acquirer_id, save_token=False, so_id=None, access_token=None, token=None, **kwargs):
        """ Json method that creates a payment.transaction, used to create a
        transaction when the user clicks on 'pay now' button. After having
        created the transaction, the event continues and the user is redirected
        to the acquirer website.

        :param int acquirer_id: id of a payment.acquirer record. If not set the
                                user is redirected to the checkout page
        """
        # Ensure a payment acquirer is selected
        if not acquirer_id:
            return False

        try:
            acquirer_id = int(acquirer_id)
        except:
            return False

        # Retrieve the sale order
        if so_id:
            env = request.env['sale.order']
            domain = [('id', '=', so_id)]
            if access_token:
                env = env.sudo()
                domain.append(('access_token', '=', access_token))
            order = env.search(domain, limit=1)
        else:
            order = request.website.sale_get_order()

        # Ensure there is something to proceed
        if not order or (order and not order.order_line):
            return False

        assert order.partner_id.id != request.website.partner_id.id

        unavailable_products = self.check_products_availabilities(order)
        if unavailable_products and isinstance(unavailable_products, list) and len(unavailable_products):
            return unavailable_products
        elif unavailable_products == 'error':
            return 'error'

        # Create transaction
        vals = {'acquirer_id': acquirer_id,
                'return_url': '/shop/payment/validate'}

        if save_token:
            vals['type'] = 'form_save'
        if token:
            vals['payment_token_id'] = int(token)

        transaction = order._create_payment_transaction(vals)

        # store the new transaction into the transaction list and if there's an old one, we remove it
        # until the day the ecommerce supports multiple orders at the same time
        last_tx_id = request.session.get('__website_sale_last_tx_id')
        last_tx = request.env['payment.transaction'].browse(last_tx_id).sudo().exists()
        if last_tx:
            PaymentProcessing.remove_payment_transaction(last_tx)
        PaymentProcessing.add_payment_transaction(transaction)
        request.session['__website_sale_last_tx_id'] = transaction.id
        return transaction.render_sale_button(order)
