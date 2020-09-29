odoo.define('product_reference_generator_bizople.sale_product', function(require) {

    $(document).ready(function() {
        var ajax = require('web.ajax');
        var rpc = require('web.rpc');
        var core = require('web.core');
        var publicWidget = require('web.public.widget');
        require('website_sale.website_sale');
        var _t = core._t;
        publicWidget.registry.WebsiteSale.include({
        	onChangeVariant: function (ev) {
                this._super.apply(this, arguments);
                var $parent = $(ev.target).closest('.js_product');
                var qty = $parent.find('input[name="add_qty"]').val();
                var combination = this.getSelectedVariantValues($parent);
                var parentCombination = $parent.find('ul[data-attribute_exclusions]').data('attribute_exclusions').parent_combination;
                var productTemplateId = parseInt($parent.find('.product_template_id').val());
                return ajax.jsonRpc('/product_code/get_combination_info', 'call', {
                    'product_template_id': productTemplateId,
                    'product_id': this._getProductId($parent),
                    'combination': combination,
                    'add_qty': parseInt(qty),
                    'pricelist_id': this.pricelistId || false,
                    'parent_combination': parentCombination,
                }).then(function (data) {
                    $('.product_ref_code').html(data)
                });

            }
        })    
    })
})