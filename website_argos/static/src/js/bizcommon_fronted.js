odoo.define('website_argos.bizcommon_frontend_js', function(require) {
    'use strict';
    var animation = require('website.content.snippets.animation');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;
    
	if($(".oe_website_sale").length === 0){
        $("div#wrap").addClass("oe_website_sale");
    }
    
	
    if ($('.product_description').length < 1) {
        $('#product_detail_tabs').find('li:first-child').find('.nav-link').addClass('active');
        var firstlink = $('#product_detail_tabs').find('li:first-child').find('.nav-link').attr('aria-controls');
        $('.product-tab .tab-pane').removeClass('active show');
        $('#'+ firstlink).addClass('active show');
    }
    
    animation.registry.website_argos_product_slider = animation.Class.extend({
        selector: ".biz_dynamic_product_slider",
        disabledInEditableMode: false,
        start: function() {
            var self = this;
            if (this.editableMode) {
                var $prod_slider = $('#wrapwrap').find('#website_argos_custom_product_slider');
                var prod_name = _t("Products Slider")
                _.each($prod_slider, function (single){
                    $(single).empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + prod_name + '</h3>\
                                                    </div>\
                                                </div>')
                });
            }
            if (!this.editableMode) {
                var slider_id = self.$target.attr('data-prod-slider-id');
                $.get("/website_argos/product_get_dynamic_slider", {
                    'slider-id': self.$target.attr('data-prod-slider-id') || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".biz_dynamic_product_slider").removeClass('o_hidden');

                        ajax.jsonRpc('/website_argos/slider_product_call', 'call', {
                            'slider_id': slider_id
                        }).then(function(res) {
                            $('div#' + res.s_id).owlCarousel({
                                margin: 10,
                                responsiveClass: true,
                                items: res.counts,
                                loop: false,
                                dots:false,
                                rows: true,
                                rowsCount: 2,
                                rewind:true,
                                nav:true,
                                navText: [
                                    '<i class="fa fa-long-arrow-left" aria-hidden="true"></i>',
                                    '<i class="fa fa-long-arrow-right" aria-hidden="true"></i>'
                                ],
                                autoplay: res.auto_slide,
                                autoplayTimeout:res.auto_play_time,
                                autoplayHoverPause:true,
                                responsive: {
                                    0: {
                                        items: 1,
                                    },
                                    420: {
                                        items: 1,
                                    },
                                    768: {
                                        items: 3,
                                    },
                                    1000: {
                                        items: res.counts,
                                    },
                                    1500: {
                                        items: res.counts,
                                    },
                                },
                            });
                            
                            setTimeout(function(){
                                var divWidth = $('.product-item .p-item-image a').width(); 
                                $('.product-item .p-item-image a').height(divWidth);
                            },400);
                            
                        });
                    }
                });
            }
        }
    });
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
                                items: 4,
                                responsive: {
                                    0: {
                                        items: 1,
                                    },
                                    420: {
                                        items: 1,
                                    },
                                    767: {
                                        items: 3,
                                    },
                                    1000: {
                                        items: 4,
                                    },
                                
                                },
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
    
    animation.registry.s_bizople_theme_blog_slider_snippet = animation.Class.extend({
        selector: ".blog_slider_owl",
        disabledInEditableMode: false,
        start: function() {
            var self = this;
            if (this.editableMode) {
                var $blog_snip = $('#wrapwrap').find('#biz_blog_slider_snippet');
                var blog_name = _t("Blog Slider")
                
                _.each($blog_snip, function (single){
                    $(single).empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + blog_name + '</h3>\
                                                    </div>\
                                                </div>')
                });
            }
            if (!this.editableMode) {
                var slider_filter = self.$target.attr('data-blog-slider-type');
                $.get("/website_argos/second_blog_get_dynamic_slider", {
                    'slider-type': self.$target.attr('data-blog-slider-type') || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".blog_slider_owl").removeClass('o_hidden');
                        ajax.jsonRpc('/website_argos/blog_image_effect_config', 'call', {
                            'slider_filter': slider_filter
                        }).then(function(res) {
                            $('#blog_2_owl_carosel').owlCarousel({
                                margin: 30,
                                items: 3,
                                loop: false,
                                dots:false,
                                autoplay: res.auto_slide,
                                autoplayTimeout:res.auto_play_time,
                                autoplayHoverPause:true,
                                nav:true,
                                navText: [
                                    '<i class="fa fa-long-arrow-left" aria-hidden="true"></i>',
                                    '<i class="fa fa-long-arrow-right" aria-hidden="true"></i>'
                                ],
                                rewind:true,
                                responsive: {
                                    0: {
                                        items: 1,
                                    },
                                    420: {
                                        items: 1,
                                    },
                                    768: {
                                        items: 3,
                                    },
                                    1000: {
                                        items: 3,
                                    },
                                    1500: {
                                        items: 3,
                                    }
                                },
                            });
                        });
                    }
                });
            }
        }
    });
    
 
    animation.registry.cat_slider_3 = animation.Class.extend({
        selector: ".cat_slider_3",
        disabledInEditableMode: false,
        start: function() {
            var self = this;
            if (this.editableMode) {
                var $cate_slider = $('#wrapwrap').find('#website_argos_custom_category_slider_3');
                var cat_name = _t("Category Slider")
                _.each($cate_slider, function (single){
                    $(single).empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="fancy">' + cat_name + '</h3>\
                                                    </div>\
                                                </div>')
                });
            }
            if (!this.editableMode) {
                var slider_id = self.$target.attr('data-cat-slider-id');
                $.get("/website_argos/category_slider_3", {
                    'slider-id': self.$target.attr('data-cat-slider-id') || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".cat_slider_3").removeClass('o_hidden');
                        $('div#carousel_category').owlCarousel({
                            loop:false,
                            margin:20,
                            nav:true,
                            navText: [
                                '<i class="fa fa-long-arrow-left" aria-hidden="true"></i>',
                                '<i class="fa fa-long-arrow-right" aria-hidden="true"></i>'
                            ],
                            autoplay:true,
                            rewind:true,
                            dots:false,
                            autoplayTimeout:2500,
                            autoplayHoverPause:true,
                            responsive:{
                                0:{
                                    items:1
                                },
                                400:{
                                    items:1
                                },
                                767:{
                                    items:3
                                },
                                992:{
                                    items:4
                                }
                            }
                        })
                    }
                });
            }
        }
    });
    
});
