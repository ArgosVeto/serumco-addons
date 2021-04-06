odoo.define('website_argos.cart_address', function(require) {
    $(document).ready(function() {

        var ajax = require('web.ajax');
        var rpc = require('web.rpc');

        $('#clinic_name').keyup(get_match_clinic);
        $('#fav_cli').click(get_fav_cli);
        $('#all_clinic').click(get_all_clinic);


/*        if (document.getElementById('fav_cli') &&  document.getElementById('fav_cli').checked){
            ajax.rpc('/update-fav-delivery-address').then(function(data){
                $(".clinic_searching").hide();
                ajax.rpc('/update-fav-delivery-address').then(function(data){
                    if (data) {
                        $(".load_fav_clinic_add_tmp").html(data);
                        ajax.rpc('/update-delivery-address').then(function(data){
                            $(".clinic_searching").hide();
                            ajax.rpc('/update-delivery-address').then(function(data){
                                if (data) {
                                    $(".load_clinic_add_tmp").html(data);
                                    ajax.rpc('/bouton-paiement').then(function(data){
                                        ajax.rpc('/bouton-paiement').then(function(data){
                                            if (data) {
                                                $(".bouton_paiement").html(data)
                                            }
                                        });
                                    });
                                }
                            })
                        });
                    }
                });
            });
       }  */

     
    if (document.getElementById('fav_cli') &&  document.getElementById('fav_cli').checked){
            ajax.rpc('/update-fav-delivery-address').then(function(data){
                $(".clinic_searching").hide();
                $(".load_fav_clinic_add_tmp").hide();
                if (data) {
                    $(".load_fav_clinic_add_tmp").html(data);
                    ajax.rpc('/update-delivery-address').then(function(data){
                    if (data) {
                        $(".load_clinic_add_tmp").html(data);
                        ajax.rpc('/bouton-paiement').then(function(data){
                         if (data) {
                            $(".bouton_paiement").html(data)
                            }
                        });
                    }
                    });
                }
                $(".load_fav_clinic_add_tmp").show();
            });
       } 
 

       function get_all_clinic(){
        var all_clinic = document.getElementById("all_clinic");
         if(all_clinic.checked){                
            $(".clinic_searching").show();
            $(".searched_clinic_detail").show();
           }
        }
        function get_fav_cli(){
            var fav_cli = document.getElementById("fav_cli");
            if(fav_cli.checked){
                $(".load_fav_clinic_add_tmp").hide();
                $(".clinic_searching").hide();
                $(".searched_clinic_detail").hide();
                ajax.rpc('/update-delivery-address').then(function(data){
                    if (data) {
                        $(".load_clinic_add_tmp").html(data)
                    }
                })
                ajax.rpc('/update-fav-delivery-address').then(function(data){
                    if (data) {
                        $(".load_fav_clinic_add_tmp").html(data)
                    }
                })
                ajax.rpc('/bouton-paiement').then(function(data){
                    if (data) {
                       $(".bouton_paiement").html(data)
                       }
                })
/*           location.reload()*/
                $(".load_fav_clinic_add_tmp").show();
            }
        }
        function get_match_clinic(){
            var $cn = $('#clinic_name').val();
            var all_clinic =  document.getElementById("all_clinic").value;
            $(".load_fav_clinic_add_tmp").hide();
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