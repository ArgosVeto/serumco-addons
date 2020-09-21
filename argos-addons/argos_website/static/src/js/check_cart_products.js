odoo.define('argos_website.check_product', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var rpc = require('web.rpc')
var session = require('web.session')

publicWidget.registry.WebsiteSale.include({
     _handleAdd: function ($form) {
        var self = this;
        this.$form = $form;
        var showModal = false;
        var ret = null;

        var productSelector = [
            'input[type="hidden"][name="product_id"]',
            'input[type="radio"][name="product_id"]:checked'
        ];

        var product_id = parseInt($form.find(productSelector.join(', ')).first().val(), 10)
        var productQuantity = parseFloat($form.find('input[name="add_qty"]').val() || 1)

        var productReady = this.selectOrCreateProduct(
            $form,
            product_id,
            $form.find('.product_template_id').val(),
            false
        );
       return this._rpc({
                route: "/shop/product/check",
                params: {
                    product_id: product_id,
                    product_qty: productQuantity
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
                   return productReady.then(function (productId) {
                        $form.find(productSelector.join(', ')).val(productId);

                        self.rootProduct = {
                            product_id: productId,
                            quantity: productQuantity,
                            product_custom_attribute_values: self.getCustomVariantValues($form.find('.js_product')),
                            variant_values: self.getSelectedVariantValues($form.find('.js_product')),
                            no_variant_attribute_values: self.getNoVariantAttributeValues($form.find('.js_product'))
                        };

                        return self._onProductReady();
                    });
               });
    },
})
})