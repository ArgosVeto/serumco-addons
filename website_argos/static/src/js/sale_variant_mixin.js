odoo.define('websiteArgos.VariantMixin', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    publicWidget.registry.WebsiteSale.include({
        _onChangeCombination: function (ev, $parent, combination) {
            var $price_total = $parent.find("#add_to_cart .product_price .oe_price .oe_currency_value");
            $price_total.text(this._priceToStr(combination.price_total));
            this._super.apply(this, arguments);
        },
        _onClickAdd: function (ev) {
            if ($(ev.currentTarget).attr('id') === 'add_to_cart') {
                ev.preventDefault();
                ev.stopPropagation();
                $('#modal_confirm_add_to_cart').modal('show');
            }
            else {
                return this._super.apply(this, arguments);
            }
        },
    });

});