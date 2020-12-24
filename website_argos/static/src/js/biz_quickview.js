odoo.define('website_argos.biz_quickview', function(require){
'use strict';

require('web.dom_ready');
var publicWidget = require('web.public.widget');
var core = require('web.core');
var ajax = require('web.ajax');
var rpc = require('web.rpc');
var _t = core._t;


var publicWidget = require('web.public.widget');

publicWidget.registry.websiteSaleCategoryMobile = publicWidget.Widget.extend({
    selector: '#o_shop_collapse_category_mobile',
    events: {
        'click .fa-chevron-right': '_onOpenClick',
        'click .fa-chevron-down': '_onCloseClick',
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {Event} ev
     */
    _onOpenClick: function (ev) {
        var $fa = $(ev.currentTarget);
        $fa.parent().siblings().find('.fa-chevron-down:first').click();
        $fa.parents('li').find('ul:first').show('normal');
        $fa.toggleClass('fa-chevron-down fa-chevron-right');
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onCloseClick: function (ev) {
        var $fa = $(ev.currentTarget);
        $fa.parent().find('ul:first').hide('normal');
        $fa.toggleClass('fa-chevron-down fa-chevron-right');
    },
});



$(document).ready(function(){
    $(document).on('click', 'a.quick_btn', function () {
        var pid = $(this).attr('data-product_template_id');
        ajax.jsonRpc('/get_prod_quick_view_details', 'call', {'prod_id':pid}).then(function(data) 
        {
            var sale = new publicWidget.registry.WebsiteSale();
            $(".quick_modal_wrap").append(data);
            $(".quick-modal-backdrop").fadeIn();
            sale.init();
            $(".quick_modal_wrap").css("display", "block");
            $("[data-attribute_exclusions]").on('change', function(event) {
                sale.onChangeVariant(event);
            });
            $("[data-attribute_exclusions]").trigger('change');
            $(".css_attribute_color input").click(function(event){   
                sale._changeColorAttribute(event);
            });

            $(".a-submit").on('click', function(event) {
                sale._onClickAdd(event);
            });

            $("a.js_add_cart_json").on('click', function(event) {
                sale._onClickAddCartJSON(event);
            });

            $("input[name='add_qty']").on('change', function(event) {
                sale._onChangeAddQuantity(event);
            });

            $(".quick_close").click(function() {
                $('.quick_modal_wrap').empty(data);
                $('.zoomContainer').remove();
            });
        });
    });
});


});
