odoo.define('website_argos.portal', function (require) {
'use strict';

var core = require('web.core');
var qweb = core.qweb;
var publicWidget = require('web.public.widget');

publicWidget.registry.portalDetails.include({
    xmlDependencies: ['/website_argos/static/src/xml/portal_account_disclaimer.xml'],
    start: function () {

        var def = this._super.apply(this, arguments);
        this._submitDisclaimer();
        return def
    },

    _adaptAddressForm: function () {
        if(this.$stateOptions){
            this._super()
        }
        else{
            return
        }
    },

    _submitDisclaimer: function(){
        var self=this;
        var submit_button = $('.my_account_submit');
        submit_button.on('click', function(e){
            var form = $('.contact-argos');
            var Form = document.querySelector('form[action="/my/account"]');
            var inputs = form.find('input');
            var selects = form.find('select');
            var formData = new FormData();

            _.each(inputs, function(input){
                formData.append(input.name, input.value);
            });
            _.each(selects, function(select){
                formData.append(select.name, select.value);
            })
            if (core.csrf_token) {
                formData.append('csrf_token', core.csrf_token);
            }
            if(Form.checkValidity()){
                $.ajax({
                    url: '/my/account',
                    type: 'POST',
                    processData: false,
                    contentType: false,
                    data: formData,
                    success:function(data, textStatus, jqXHR){
                        $('#portal_disclaimer_container').html(qweb.render("website_argos.portal_account_disclaimer", {}))
                        $([document.documentElement, document.body]).animate({
                            scrollTop: $("#portal_disclaimer_container").parent().offset().top
                        }, 500);
                    },
                    error: function(jqXHR, textStatus, errorThrown){

                    }
                });
            }
            else if(!Form.checkValidity()){
                 Form.reportValidity();
            }

        });
    },
})

})