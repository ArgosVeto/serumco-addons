odoo.define('website_map.slider_js', function(require) {
    'use strict';
    var animation = require('website.content.snippets.animation');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;

    animation.registry.s_bizople_theme_multi_product_tab_snippet = animation.Class.extend({
        selector: ".oe_multi_category_slider",
        disabledInEditableMode: false,
        start: function() {
            var self = this;
            if (this.editableMode) {
                var $multi_cat_slider = $('#wrapwrap').find('.oe_multi_category_slider');
                var multi_cat_name = _t("Multi Product Slider")

                _.each($multi_cat_slider, function (single){
                    $(single).empty().append('<div class="container">\
                                                <div class="row our-categories">\
                                                    <div class="col-md-12">\
                                                        <div class="title-block">\
                                                            <h4 id="snippet-title" class="section-title style1"><span>'+ multi_cat_name+'</span></h4>\
                                                        </div>\
                                                    </div>\
                                                </div>\
                                            </div>')
                });

            }
            if (!this.editableMode) {
                var slider_filter = self.$target.attr('data-multi-cat-slider-type');
                $.get("/tabpro/product_multi_get_dynamic_slider", {
                    'slider-type': self.$target.attr('data-multi-cat-slider-type') || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".oe_multi_category_slider").removeClass('hidden');

                        ajax.jsonRpc('/website_argos/multi_tab_product_call', 'call', {
                            'slider_filter': slider_filter
                        }).then(function(res) {
                            $('div.product_tab_slider_owl .owl-carousel').owlCarousel({
                                loop:false,
                                dots:false,
                                autoplay: res.auto_slide,
                                autoplayTimeout:res.auto_play_time,
                                autoplayHoverPause:true,
                                margin:30,
                                nav:true,
                                navText: [
                                    '<i class="fa fa-long-arrow-left" aria-hidden="true"></i>',
                                    '<i class="fa fa-long-arrow-right" aria-hidden="true"></i>'
                                ],
                                rewind:true,
                                items: 1,

                            });
                            setTimeout(function(){
                                var divWidth = $('.product_tab_slider_owl .product-item .p-item-image a').width(); 
                                $('.product_tab_slider_owl .product-item .p-item-image a').height(divWidth);
                            },400);
                        });

                    }
                });
            }
        }
    });
});
