odoo.define('website_argos.cart_address', function(require) {
    $(document).ready(function() {

        var ajax = require('web.ajax');
        var rpc = require('web.rpc');

        $('#clinic_name').keyup(get_match_clinic);
        $('#fav_cli').click(get_fav_cli);
        $('#all_clinic').click(get_all_clinic);


        if (document.getElementById('fav_cli') &&  document.getElementById('fav_cli').checked){
            ajax.rpc('/update-delivery-address').then(function(data){
                $(".clinic_searching").hide();
                ajax.rpc('/update-delivery-address').then(function(data){
                    if (data) {
                        $(".load_clinic_add_tmp").html(data)
                    }
                })
            });
        }
        
        function get_all_clinic(){
            var all_clinic = document.getElementById("all_clinic");
             if(all_clinic.checked){                
                $(".clinic_searching").show();
            }
        }

        function get_fav_cli(){
            var fav_cli = document.getElementById("fav_cli");
             if(fav_cli.checked){
                $(".clinic_searching").hide();
                ajax.rpc('/update-delivery-address').then(function(data){
                    if (data) {
                        $(".load_clinic_add_tmp").html(data)
                    }
                })
            }
        }
        function get_match_clinic(){
            var $cn = $('#clinic_name').val();
            var all_clinic =  document.getElementById("all_clinic").value;
            if($cn.length >= 1){
                ajax.rpc('/find-matched-clinic',{'cn':$cn}).then(function(data){
                    if (data) {
                        $("#searched_clinic_detail").html(data)
                    }
                })
            }
            else{
                ajax.rpc('/find-matched-clinic',{}).then(function(data){
                    if (data) {
                        $("#searched_clinic_detail").html(data)
                    }
                })
            }
        }
    });
})