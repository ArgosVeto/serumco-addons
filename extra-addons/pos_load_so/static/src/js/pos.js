odoo.define('pos_quotations.pos_quotations', function (require) {
"use strict";

	var module = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var PosPopWidget = require('point_of_sale.popups');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;
    var _t = core._t;



	var _super_order = module.Order.prototype;
    module.Order = module.Order.extend({
        initialize: function() {
            _super_order.initialize.apply(this,arguments);
            this.save_to_db();
            this.quot_id = false;
        },
        export_as_JSON: function() {
            var json = _super_order.export_as_JSON.apply(this,arguments);
            json.quot_id = this.quot_id;
            return json;
        },
        init_from_JSON: function(json) {
            _super_order.init_from_JSON.apply(this,arguments);
            this.quot_id = json.quot_id;
        },
    });    
    
	var SaleOrderListScreenWidget = screens.ScreenWidget.extend({
	    template: 'SaleOrderListScreenWidget',

	    auto_back: true,
	    renderElement: function() {
	        var self = this;
	        this._super();
	       	this.$('.back').click(function(){
	            self.gui.back();
	        });
	        var search_timeout = null;
	       	this.$('.searchbox input').on('keyup',function(event){
	            var query = this.value;
	            if(query==""){
	            	self.render_list(self.pos.quotations);
	            }
	            else{
	            	self.perform_search(query);
	            }
	        });
	        this.$('.client-list-contents').delegate('.wv_checkout_button','click',function(event){
            	var quotation = self.get_quotations_by_id($(this).data('id'));
            	var order = self.pos.get_order();
	            var orderlines = order.get_orderlines();
		        if(orderlines.length == 0){
			        rpc.query({
	                    model: 'sale.order',
	                    method: 'quotation_fetch_line',
	                    args: [quotation.id],
	                }).then(function(quotation_data){
			            order.set('client',undefined);
			            order.quotation_id = quotation.name;
			            order.quot_id = quotation.id;
			            if(quotation.partner_id){
			            	order.set_client(self.pos.db.get_partner_by_id(quotation.partner_id[0]));
			            }
			            for(var i=0;i<quotation_data.length;i++){
		            		var product = self.pos.db.get_product_by_id(quotation_data[i]['product_id'][0]);
		            		if(product){
		            			order.add_product(product,{'quantity':quotation_data[i]['product_uom_qty']});
		            		}
		            	}
		            	self.gui.back();
			        },function(err,event){
			            event.preventDefault();
			            self.gui.show_popup('error',{
			                'title': _t('Error: Could not Save Changes'),
			                'body': _t('Your Internet connection is probably down.'),
			            });
			        });
		    }
		    else{
		    	self.gui.show_popup('error',{
		                'title': _t('Error: Could not Check-Out Order'),
		                'body': _t('Please remove all products from cart and try again.'),
			        });
		    }
		});
	    },
	    show: function(){
	        var self = this;
	        this._super();
	        this.renderElement();
	        // this.details_visible = false;
	        // this.old_client = this.pos.get_order().get_client();
	        this.render_list(self.pos.quotations);
	    },

	    perform_search: function(query){
	    	var quotations = this.pos.quotations;
	    	var results = [];
	        for(var i = 0; i < quotations.length; i++){
	        	var res = this.search_quotations(query, quotations[i]);
	        	if(res != false){
	        	results.push(res);
	        }
	        }
	        this.render_list(results);
	    },
	    search_quotations: function(query,quotations){
	        try {
	            query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
	            query = query.replace(' ','.+');
	            var re = RegExp("([0-9]+):.*?"+query,"gi");
	        }catch(e){
	            return [];
	        }
	        var results = [];
            var r = re.exec(this._quotations_search_string(quotations));
            if(r){
                var id = Number(r[1]);
                return this.get_quotations_by_id(id);
            }
	        return false;
	    },
	    get_quotations_by_id:function(id){
	    	var quotations = this.pos.quotations;
	    	for(var i=0;i<quotations.length;i++){
	    		if(quotations[i].id == id){
	    			return quotations[i];
	    		}
	    	}
	    },
	    _quotations_search_string: function(quotations){
		        var str =  quotations.name;
		        if(quotations.partner_id){
		            str += '|' + quotations.partner_id[1];
		        }
		        str = '' + quotations.id + ':' + str.replace(':','') + '\n';
		        return str;
		    },
	    render_list: function(quotationsVal){
	    	var self = this;
	        var contents = this.$el[0].querySelector('.client-list-contents');
	        contents.innerHTML = "";
	        var quotations = quotationsVal;
	        for(var i = 0;i<quotations.length; i++){
	            var quotation    = quotations[i];
                var clientline_html = QWeb.render('SaleOrderLine',{widget: self, quotation:quotation});
                var clientline = document.createElement('tbody');
                clientline.innerHTML = clientline_html;
                clientline = clientline.childNodes[1];
	            contents.appendChild(clientline);
	        }
	    },

	    close: function(){
	        this._super();
	    },
	});
	gui.define_screen({name:'sale-order-list', widget: SaleOrderListScreenWidget});


	var SaleOrderListButton = screens.ActionButtonWidget.extend({
        template: 'SaleOrderListButton',
        button_click: function(){
        	var self = this;
        	var quotation = this.pos.quotations;
        	var available_qt = []
        	var config_id = self.pos.config.id;
        	var from = moment(new Date()).subtract(self.pos.config.sale_order_days,'d').format('YYYY-MM-DD')+" 00:00:00";
			rpc.query({
                model: 'sale.order',
                method: 'new_sent_order_json',
                args: [from,config_id],
            }).then(function(result){
        			self.pos.quotations = [];
					var quot_data = result['data']
					for(var k=0;k<quot_data.length;k++){
						self.pos.quotations.push(quot_data[k][0]);
					}
				self.gui.show_screen('sale-order-list',{},'refresh');

		        },function(err,event){
		            event.preventDefault();
		            self.gui.show_popup('error',{
		                'title': _t('Error: Could not Save Changes'),
		                'body': _t('Your Internet connection is probably down.'),
		            });
		      });

        },
    });
	screens.define_action_button({
        'name': 'Sale Order List',
        'widget': SaleOrderListButton,
        'condition': function(){
            return this.pos.config.allow_load_so;
        },
    });

});
