odoo.define('argos_website.recently_viewed', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var wSaleUtils = require('website_sale.utils');

publicWidget.registry.productsRecentlyViewedSnippet.include({
     _onAddToCart: function (ev) {
        var self = this;
        var $card = $(ev.currentTarget).closest('.card');
        var product_id = $card.find('input[data-product-id]').data('product-id')

        this._rpc({
            route: "/shop/product/check",
            params: {
                product_id: product_id,
                product_qty: 1,
            },
        }).then(function (result) {
            if (result.status == 'no') {
                $('#unavailableProductModal').modal('show')
                return false
            }
            else if (result.status == 'error') {
                $('#errorServiceModal').modal('show')
                return false
            }
           self._rpc({
                route: "/shop/cart/update_json",
                params: {
                    product_id: product_id,
                    add_qty: 1
                },
            }).then(function (data) {
                wSaleUtils.updateCartNavBar(data);
                var $navButton = wSaleUtils.getNavBarButton('.o_wsale_my_cart');
                var fetch = self._fetch();
                var animation = wSaleUtils.animateClone($navButton, $(ev.currentTarget).parents('.o_carousel_product_card'), 25, 40);
                Promise.all([fetch, animation]).then(function (values) {
                    self._render(values[0]);
                });
            });
        });
    },
})
})