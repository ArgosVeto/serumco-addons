var myLatLng;
var jobLatLng;
function around_func(){
 var jobaround = document.getElementById("around_me3");
        jobaround.onclick = function(){
            document.getElementById("googleMap2").style.display = "block";
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
function around_me() {
odoo.define('website_map.arounded', function (require) {
    var rpc = require('web.rpc')  
    $('.around').ready(function initMap() {
        var clinic_grid = document.getElementsByClassName('clinic_grid');
        for (i=0; i<clinic_grid.length;i++){
          if (clinic_grid[i].classList.contains("col-lg-4")) {
            
            clinic_grid[i].classList.remove("col-lg-4");
            clinic_grid[i].classList.add("col-lg-5");
          }          
        }
        myLatLng={ lat: 44.837789, lng: -0.57918 };
        var map = new google.maps.Map(document.getElementById("googleMap"), {
          zoom: 10,
          center: myLatLng,
        });
      });
    document.getElementById("googleMap").style.display = "block";
            loca = getLocation(function (position) {
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
                if (locations/1000 <= 50){

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

        
});
}
function gMap() {
odoo.define('website_map.googleMap', function (require) {
    var rpc = require('web.rpc');
     $('.googleMap').ready(function initMap() {
        myLatLng={ lat: 44.837789, lng: -0.57918 };
        var clinic_grid = document.getElementsByClassName('clinic_grid');
        for (i=0; i<clinic_grid.length;i++){
          if (clinic_grid[i].classList.contains("col-lg-4")) {
            
            clinic_grid[i].classList.remove("col-lg-4");
            clinic_grid[i].classList.add("col-lg-5");
          }          
        }
        var map = new google.maps.Map(document.getElementById("googleMap"), {
          zoom: 10,
          center: myLatLng,
        });
        var around = document.getElementById("around_me")
        around.onclick = function(){
            getLocation(function (position) {
            document.getElementById("googleMap").style.display = "block";
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
let markers = [];
var add;
var map;
var citylng;

odoo.define('website_map.arounded_detailed', function (require) {
  var rpc = require('web.rpc')

  getLocation(function (position) {
            rpc.query({
          model: 'operating.unit',
          method: 'clinic_detail'
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
                    citylng = myLatLng2
                }
                var map=false;
//                if (document.getElementById("googleMap_clinic")){
//                  var map = new google.maps.Map(document.getElementById("googleMap_clinic"), {
//                      zoom: 10,
//                      center: new google.maps.LatLng(44.837789,-0.57918),
//                    });
//                    }
                const marker = new google.maps.Marker({
                        position: myLatLng2,
                        // label:cities,
                        map,
                        center:myLatLng2,
                        zoom:10,
                    });
                markers.push(marker);
            });
          })
        })

//onclick function end

    });
//$("#i_go").click(function() {
//    getLocation(function (position) {
//    var myLatLng={lat:position.coords.latitude,lng:position.coords.longitude}
//    const directionsService = new google.maps.DirectionsService();
//    const directionsRenderer = new google.maps.DirectionsRenderer();
//    directionsRenderer.setMap(map);
//    directionsService.route(
//    {
//      origin: myLatLng,
//      destination: citylng,
//      travelMode: google.maps.TravelMode.DRIVING,
//    },
//    (response, status) => {
//      if (status === "OK") {
//        deleteMarkers();
//        directionsRenderer.setDirections(response);
//      } else {
//        window.alert("Sorry! unable to find route");
//      }
//    }
//  );
//
//});
//  });
});
function setMapOnAll(map) {
  for (let i = 0; i < markers.length; i++) {
    markers[i].setMap(map);
  }
}
function deleteMarkers() {
  setMapOnAll(null);
  markers = [];
}