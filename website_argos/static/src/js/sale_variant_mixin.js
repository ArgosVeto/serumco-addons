odoo.define('websiteArgos.VariantMixin', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    publicWidget.registry.WebsiteSale.include({
        events: _.extend({}, publicWidget.registry.WebsiteSale.prototype.events,{
            'click label.alt_product_radio[data-url]': '_onClickAltProductRadio',
        }),
        _onChangeCombination: function (ev, $parent, combination) {
            var $price_total = $parent.find("#add_to_cart .product_price .oe_price .oe_currency_value");
            $price_total.text(this._priceToStr(combination.price_total));
            this._super.apply(this, arguments);
        },
        _onClickAltProductRadio: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var $alt_product = $(ev.currentTarget);
            window.location.replace($alt_product.data('url'));
        }
    });

});