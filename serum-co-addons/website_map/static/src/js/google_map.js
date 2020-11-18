var myLatLng;
var jobLatLng;
function around_func(){
 var jobaround = document.getElementById("around_me3");
        jobaround.onclick = function(){
            getLocation(function(pos){
                var jobLatLng = {lat:pos.coords.latitude,lng:pos.coords.longitude}
                var map = new google.maps.Map(document.getElementById("googleMap2"), {
                  zoom: 10,
                  center: jobLatLng,
                }); 
              });
          }
        }
function getLocation(callback) {
  if (navigator.geolocation) {
    myLatLng=navigator.geolocation.getCurrentPosition(callback);
  } 
  else { 
    x.innerHTML = "Geolocation is not supported by this browser.";
  }
}
function jobMap(){
odoo.define('website_map.googleMapjob',function(require){
var rpc = require('web.rpc')
    $('.googleMapjob').ready(function initMapjob() {
        jobLatLng={ lat: 46.603354, lng: 1.8883335 };
        var map = new google.maps.Map(document.getElementById("googleMapjob"), {
          zoom: 10,
          center: jobLatLng,
        });
        var jobaround = document.getElementById("around");
        jobaround.onclick = function(){
            getLocation(function(pos){
                var jobLatLng = {lat:pos.coords.latitude,lng:pos.coords.longitude}
                var map = new google.maps.Map(document.getElementById("googleMapjob"), {
                  zoom: 10,
                  center: jobLatLng,
                });
                rpc.query({
          model: 'hr.job',
          method: 'job_detail_json'
        }).then(function (data){
          $.each(data, function(key, val){
            var geocoders = new google.maps.Geocoder();
            var cities = val['city']
            // var names = val['name']
            geocoders.geocode({'address': cities}, function(results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                    var latitude = results[0].geometry.location.lat();
                    var longitude = results[0].geometry.location.lng();
                    var jobLatLng2 = { lat: latitude, lng: longitude };
                }
                var locations = google.maps.geometry.spherical.computeDistanceBetween(
                    new google.maps.LatLng(jobLatLng2),new google.maps.LatLng(jobLatLng));
                if (locations/1000 <= 50){

                    new google.maps.Marker({
                        position: jobLatLng2,
                        // label:names,
                        map,
                        zoom:10,
                    });
                }
            });
          })
        })
        //onclick ends here
            });
        };
    });
});
};
function gMap() {
odoo.define('website_map.googleMap', function (require) {
    var rpc = require('web.rpc')
     $('.googleMap').ready(function initMap() {
        myLatLng={ lat: 46.603354, lng: 1.8883335 };
        var map = new google.maps.Map(document.getElementById("googleMap"), {
          zoom: 10,
          center: myLatLng,
        });
        var around = document.getElementById("around_me")
        around.onclick = function(){
            getLocation(function (position) {
            var myLatLng={lat:position.coords.latitude,lng:position.coords.longitude}
            var map = new google.maps.Map(document.getElementById("googleMap"), {
              zoom: 10,
              center: myLatLng,
            });
            rpc.query({
          model: 'operating.unit',
          method: 'clinic_detail_json'
        }).then(function (data){
          $.each(data, function(key, val){
            var geocoders = new google.maps.Geocoder();
            var cities = val['city']
            // var names = val['name']
            geocoders.geocode({'address': cities}, function(results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                    var latitude = results[0].geometry.location.lat();
                    var longitude = results[0].geometry.location.lng();
                    var myLatLng2 = { lat: latitude, lng: longitude };
                }
                var locations = google.maps.geometry.spherical.computeDistanceBetween(
                    new google.maps.LatLng(myLatLng2),new google.maps.LatLng(myLatLng));
                if (locations/1000 <= 100){

                    new google.maps.Marker({
                        position: myLatLng2,
                        // label:names,
                        map,
                        zoom:10,
                    });
                }
            });
          })
        })

//onclick function end

    });

        }
        
        var self = this;
        rpc.query({
          model: 'operating.unit',
          method: 'clinic_detail_json'
        }).then(function (data){
          $.each(data, function(key, val){
            var geocoder = new google.maps.Geocoder();
            var city = val['city']
            // var name = val['name']
            var geocoder = new google.maps.Geocoder();
            geocoder.geocode({'address': city}, function(results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                    var latitude = results[0].geometry.location.lat();
                    var longitude = results[0].geometry.location.lng();
                    var myLatLng1 = { lat: latitude, lng: longitude };
                } 
                new google.maps.Marker({
                    position: myLatLng1,
                    // label:name,
                    map,
                    zoom:10,
                });
            });
          })
        })
    });
});
};