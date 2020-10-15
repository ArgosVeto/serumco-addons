$(document).ready(function(){

  if ($("nav").hasClass("o_portal_navbar")) {
    $('.ac-order').addClass('active-order'); 
  }

  if ($("div").hasClass("no-gutters")) {
    $('.ac-address').addClass('active-address'); 
  }

  if ($("div").hasClass("o_portal_my_home")) {
    $('.ac-info').addClass('active-info'); 
  }
	
	$(function() {
		setTimeout(function(){ 
			$('#vetowidget iframe html').append('<link rel="stylesheet" href="/website_argos/static/src/css/appointment.css" type="text/css" />');
			
		}, 3000);
		
	});
	
	
	window.onload = function() {
		  let frameElement = document.getElementById("myiFrame");
		  let doc = frameElement.contentDocument;
		  doc.body.innerHTML = doc.body.innerHTML + '<style>.bar {width:45%;}</style>';
		}
	
	
	$(function() {
      var a = 0;
      $(window).scroll(function() {
        if ($(this).scrollTop() > 100) {
          if ( $('.counter-box').length > 0 ) {
            var oTop = $('.counter-box').offset().top - window.innerHeight;
            if (a == 0 && $(window).scrollTop() > oTop) {
              $('.counter').each(function () {
                $(this).prop('Counter',0).animate({
                    Counter: $(this).text()
                }, {
                    duration: 4000,
                    easing: 'swing',
                    step: function (now) {
                        $(this).text(Math.ceil(now));
                    }
                  });
              }); 
              a = 1;
            }
          }
        } 
      });
      
    });
	
    $(function() {
      $(window).scroll(function() {
        if ($(this).scrollTop() > 100) {
          $('a.top').addClass('show-to-top');
        } else {
          $('a.top').removeClass('show-to-top');
        }
      });
      $('#to-top a').click(function() {
        $('body,html').animate({
          scrollTop : 0
        }, 800);
        return false;
      });
    });

    $(function() {
      $(window).scroll(function() {
        if ($(this).scrollTop() > 100) {
          $('.header-search-bar').addClass('fixed-search');
        } else {
          $('.header-search-bar').removeClass('fixed-search');
        }
      });
    });

    $(function() {
      $(window).scroll(function() {
        if ($(this).scrollTop() > 100) {
          $('.bizople-mbl-bottom-bar').addClass('show-bottom-bar');
        } else {
          $('.bizople-mbl-bottom-bar').removeClass('show-bottom-bar');
        }
      });
    });
    $(function() {
      $(window).scroll(function() {
        if ($(this).scrollTop() > 982) {
          $('.clinic-detail-sticky').addClass('side-sticky')
        } else {
          $('.clinic-detail-sticky').removeClass('side-sticky')
        }
      });
    });

    $("a.active").find('.mycheckbox').prop('checked', true);
    
    // Price slider code start
    var minval = $("input#m1").attr('value'),
        maxval = $('input#m2').attr('value'),
        minrange = $('input#ra1').attr('value'),
        maxrange = $('input#ra2').attr('value'),
        website_currency = $('input#estore_website_currency').attr('value');
    if (!minval) {
        minval = 0;
    }
    if (!maxval) {
        maxval = maxrange;
    }
    if (!minrange) {
        minrange = 0;

    }
    if (!maxrange) {
        maxrange = 2000;
    }

    $("div#priceslider").ionRangeSlider({
        keyboard: true,
        min: parseInt(minrange),
        max: parseInt(maxrange),
        type: 'double',
        from: minval,
        skin: "square",
        to: maxval,
        step: 1,
        prefix: website_currency,
        grid: true,
        onFinish: function(data) {
            $("input[name='min1']").attr('value', parseInt(data.from));
            $("input[name='max1']").attr('value', parseInt(data.to));
            $("div#priceslider").closest("form").submit();
        },
    });

    $('[data-toggle="popover"]').popover()
});

$(function() {
  /* menu sidebar js */
  $("#show-sidebar").on("click", function(e) {
    $(".sidebar-wrapper").addClass("toggled");
    e.stopPropagation()
  });
  $(".bottom-show-sidebar").on("click", function(e) {
    $(".sidebar-wrapper").addClass("toggled");
    e.stopPropagation()
  });
  $("#close_mbl_sidebar").on("click", function(e) {
    $(".sidebar-wrapper").removeClass("toggled");
    e.stopPropagation()
  });
  $(document).on("click", function(e) {
    if (!$(e.target).closest('.sidebar-wrapper').length) {
      $(".sidebar-wrapper").removeClass("toggled");
    }
  });


  /* cart sidebar js */
  $(".show_cart_sidebar").on("click", function(e) {
    $("#cart_sidebar").addClass("toggled");
    e.stopPropagation()
  });
  $(".show_cart_sidebar_mbl").on("click", function(e) {
    $("#cart_sidebar").addClass("toggled");
    e.stopPropagation()
  });
  $(".show_cart_sidebar_btm_bar").on("click", function(e) {
    $("#cart_sidebar").addClass("toggled");
    e.stopPropagation()
  });
  $("#close_cart_sidebar").on("click", function(e) {
    $("#cart_sidebar").removeClass("toggled");
    e.stopPropagation()
  });
  $(document).on("click", function(e) {
    if (!$(e.target).closest('#cart_sidebar').length) {
      $("#cart_sidebar").removeClass("toggled");
    }
  });

  /* category sidebar js */
  $(".filter_btn").on("click", function(e) {
    $(".category-sidebar").addClass("toggled");
    e.stopPropagation()
  });
  $(".bottom_bar_filter_button").on("click", function(e) {
    $(".category-sidebar").addClass("toggled");
    e.stopPropagation()
  });
  $("#category_close").on("click", function(e) {
    $(".category-sidebar").removeClass("toggled");
    e.stopPropagation()
  });
  $(document).on("click", function(e) {
    if (!$(e.target).closest('.category-sidebar').length) {
      $(".category-sidebar").removeClass("toggled");
    }
  });


});

/*show more btn js for category*/

$(function() {
    var list_height = $('.category-height-overflow').height();
    if(list_height > 60){
        var text = $('.category-height-overflow'),
        btn = $('.show-more-btn');
        h = text[0].scrollHeight;
        if(h > 60) {
            btn.addClass('less');
            btn.css('display', 'block');
        }

        btn.click(function(e)
        {
            e.stopPropagation();
            var target = $(e.target);
            var text = $('.category-height-overflow'),
            btn = $(this);
            h = text[0].scrollHeight;
          if ($(target).hasClass('less')) {
              $(target).removeClass('less');
              $(target).addClass('more');
              $(target).text('- Show less');
              text.animate({'height': h});
          }else {
              $(target).addClass('less');
              $(target).removeClass('more');
              $(target).text('+ Show more');
              text.animate({'height': '220px'});
          }
        });
    }
});

/*show more btn js for radio attribute*/
$(function() {
    var radio_list_height = $('.radio-height-overflow').height();
    if(radio_list_height > 60){
        var text = $('.radio-height-overflow'),
        btn = $('.radio-show-more-btn');
        h = text[0].scrollHeight;
        if(h < 60) {
            btn.addClass('less');
            btn.css('display', 'block');

        }

        btn.click(function(e)
        {
            e.stopPropagation();
            var target = $(e.target);
            var text = $(target).prev('.radio-height-overflow');
            btn = $(this);
            h = text[0].scrollHeight;
          if ($(target).hasClass('less')) {
              $(target).removeClass('less');
              $(target).addClass('more');
              $(target).text('- Show less');
              text.animate({'height': h});
          }else {
              $(target).addClass('less');
              $(target).removeClass('more');
              $(target).text('+ Show more');
              text.animate({'height': '165px'});
          }
        });
    }
});

/*show more btn js for color attribute*/
$(function() {
    var color_list_height = $('.color-height-overflow').height();
    if(color_list_height > 60){
        var text = $('.color-height-overflow'),
        btn = $('.color-show-more-btn');
        h = text[0].scrollHeight;
        if(h < 60) {
            btn.addClass('less');
            btn.css('display', 'block');

        }

        btn.click(function(e)
        {
            e.stopPropagation();
            var target = $(e.target);
            var text = $(target).prev('.color-height-overflow');
            btn = $(this);
            h = text[0].scrollHeight;
          if ($(target).hasClass('less')) {
              $(target).removeClass('less');
              $(target).addClass('more');
              $(target).text('- Show less');
              text.animate({'height': h});
          }else {
              $(target).addClass('less');
              $(target).removeClass('more');
              $(target).text('+ Show more');
              text.animate({'height': '155px'});
          }
        });
    }
});

$(function() {
    var color_list_height = $('.brand-height-overflow').height();
    if(color_list_height > 60){
        var text = $('.brand-height-overflow'),
        btn = $('.brand-show-more-btn');
        h = text[0].scrollHeight;
        if(h < 60) {
            btn.addClass('less');
            btn.css('display', 'block');

        }

        btn.click(function(e)
        {
            e.stopPropagation();
            var target = $(e.target);
            var text = $(target).prev('.brand-height-overflow');
            btn = $(this);
            h = text[0].scrollHeight;
          if ($(target).hasClass('less')) {
              $(target).removeClass('less');
              $(target).addClass('more');
              $(target).text('- Show less');
              text.animate({'height': h});
          }else {
              $(target).addClass('less');
              $(target).removeClass('more');
              $(target).text('+ Show more');
              text.animate({'height': '172px'});
          }
        });
    }
});

/* header category menu --- submenu*/
$(function() {
    var categ_target = $(".estore-header-category > li.dropdown-submenu > i.ti");
    var parent_categ = $(categ_target).parent();
    if ($(categ_target).hasClass("ti")) {
        $(parent_categ).addClass('dropright');
    }
});

/* shop page grid */
function grid4(){
    if ($(".estore_product_pager .o_wsale_apply_layout .grid4").hasClass("active")) {
      $(".estore_shop #products_grid").removeClass("sale_layout_grid4");
    }else {
      $(".estore_shop #products_grid").addClass("sale_layout_grid4");
      localStorage.setItem("class", "sale_layout_grid4");
      $(".estore_shop #products_grid").removeClass("o_wsale_layout_list");
      $(".estore_shop #products_grid").removeClass("sale_layout_grid3");
      $(".estore_product_pager .o_wsale_apply_layout .sale_list").removeClass("active");
      $(".estore_product_pager .o_wsale_apply_layout .grid3").removeClass("active");
      $(".estore_shop #products_grid").removeClass("sale_layout_grid2");
      $(".estore_product_pager .o_wsale_apply_layout .grid2").removeClass("active");
    }
};

function grid3(){
    if ($(".estore_product_pager .o_wsale_apply_layout .grid3").hasClass("active")) {
      $(".estore_shop #products_grid").removeClass("sale_layout_grid3");
    }else {
      $(".estore_shop #products_grid").addClass("sale_layout_grid3");
      localStorage.setItem("class", "sale_layout_grid3");
      $(".estore_shop #products_grid").removeClass("o_wsale_layout_list");
      $(".estore_product_pager .o_wsale_apply_layout .sale_list").removeClass("active");
      $(".estore_shop #products_grid").removeClass("sale_layout_grid4");
      $(".estore_product_pager .o_wsale_apply_layout .grid4").removeClass("active");
      $(".estore_shop #products_grid").removeClass("sale_layout_grid2");
      $(".estore_product_pager .o_wsale_apply_layout .grid2").removeClass("active");
    }
};

function grid2(){
    if ($(".estore_product_pager .o_wsale_apply_layout .grid2").hasClass("active")) {
      $(".estore_shop #products_grid").removeClass("sale_layout_grid2");
    }else {
      $(".estore_shop #products_grid").addClass("sale_layout_grid2");
      localStorage.setItem("class", "sale_layout_grid2");
      $(".estore_shop #products_grid").removeClass("o_wsale_layout_list");
      $(".estore_product_pager .o_wsale_apply_layout .sale_list").removeClass("active");
      $(".estore_shop #products_grid").removeClass("sale_layout_grid4");
      $(".estore_product_pager .o_wsale_apply_layout .grid4").removeClass("active");
      $(".estore_shop #products_grid").removeClass("sale_layout_grid3");
      $(".estore_product_pager .o_wsale_apply_layout .grid3").removeClass("active");
    }
};

function salelist(){
    if ($(".estore_product_pager .o_wsale_apply_layout .sale_list").hasClass("active")) {
      $(".estore_shop #products_grid").removeClass("o_wsale_layout_list");
    }else {
      $(".estore_shop #products_grid").addClass("o_wsale_layout_list");
      localStorage.setItem("class", "o_wsale_layout_list");
      $(".estore_shop #products_grid").removeClass("sale_layout_grid3");
      $(".estore_product_pager .o_wsale_apply_layout .grid3").removeClass("active");
      $(".estore_shop #products_grid").removeClass("sale_layout_grid4");
      $(".estore_product_pager .o_wsale_apply_layout .grid4").removeClass("active");
      $(".estore_shop #products_grid").removeClass("sale_layout_grid2");
      $(".estore_product_pager .o_wsale_apply_layout .grid2").removeClass("active");
    }
};

function SetClass() {
//before assigning class check local storage if it has any value
    $(".estore_shop #products_grid").addClass(localStorage.getItem("class"));
    ActiveClass();
}

function ActiveClass() {
    if ($(".estore_shop #products_grid").hasClass("o_wsale_layout_list")) {
      $(".estore_product_pager .o_wsale_apply_layout .sale_list").addClass("active");
    }else if ($(".estore_shop #products_grid").hasClass("sale_layout_grid3"))  {
      $(".estore_product_pager .o_wsale_apply_layout .grid3").addClass("active");
    }else if ($(".estore_shop #products_grid").hasClass("sale_layout_grid4"))  {
      $(".estore_product_pager .o_wsale_apply_layout .grid4").addClass("active");
    }else if ($(".estore_shop #products_grid").hasClass("sale_layout_grid2"))  {
      $(".estore_product_pager .o_wsale_apply_layout .grid2").addClass("active");
    }
}

$(function() {
    SetClass();
});


$(function() {
    if ($('.estore_shop').hasClass('estore_shop')) {
      $('.bottom-bar-filter').removeClass('d-none');
      $('.bottom-bar-shop').addClass('d-none');
    }else {
      $('.bottom-bar-filter').addClass('d-none');
      $('.bottom-bar-shop').removeClass('d-none');
    }
});

$(function() {
  if ($('.o_wsale_layout_list').hasClass('o_wsale_layout_list')) {
    $('.o_wsale_layout_list').addClass('col-lg-9');
  }else {
    $('.o_wsale_layout_list').removeClass('col-lg-9');
  }
});

$(function() {
  $('.o_wsale_product_information .list-unstyled  li:first .radio_input_value').addClass('active');
  var input_target = $('.o_wsale_product_information .js_variant_change')
  input_target.click(function(e){
      if ($('.o_wsale_product_information .radio_input_value').hasClass('active')) {
        $('.o_wsale_product_information .radio_input_value').removeClass('active');
      }
      var target = $(e.target);
      var next = $(target).next();
      if ($(next).hasClass('active')) {
        $(next).removeClass('active');
      } else {
        $(next).addClass('active');
      }
  });
});

$(function() {
  $('.variant_attribute  .list-unstyled  li:first .radio_input_value').addClass('active');
  var input_target = $('.variant_attribute .js_variant_change')
  input_target.click(function(e){
      if ($('.variant_attribute .radio_input_value').hasClass('active')) {
        $('.variant_attribute .radio_input_value').removeClass('active');
      }
      var target = $(e.target);
      var next = $(target).next();
      if ($(next).hasClass('active')) {
        $(next).removeClass('active');
      } else {
        $(next).addClass('active');
      }
  });
});
