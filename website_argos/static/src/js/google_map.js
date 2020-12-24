function gMap() {
odoo.define('website_argos.googleMap', function (require) {
    var rpc = require('web.rpc')
     $('.googleMap').ready(function initMap() {
        const myLatLng = { lat: 46.603354, lng: 1.8883335 };
        const map = new google.maps.Map(document.getElementById("googleMap"), {
          zoom: 6,
          center: myLatLng,
        });
        // var url = window.location.href;
        // var c = url.searchParams.get("operating_unit.street");
        // console.log("uuuuuuuuuuuuuuuuuuuuuuuuuuu",url);
        var self = this;
        rpc.query({
          model: 'operating.unit',
          method: 'clinic_detail_json'
        }).then(function (data){
          // console.log("============", data);
          $.each(data, function(key, val){
            var geocoder = new google.maps.Geocoder();
            var city = val['city']
            var name = val['name']
            // console.log("$$$$$$$$$$$$$$", city)
            var geocoder = new google.maps.Geocoder();
            geocoder.geocode({'address': city}, function(results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                    var latitude = results[0].geometry.location.lat();
                    var longitude = results[0].geometry.location.lng();
                    // console.log("ppppppppppppplllllllll",latitude,longitude);
                    var myLatLng1 = { lat: latitude, lng: longitude };
                } 
                new google.maps.Marker({
                    position: myLatLng1,
                    label:name,
                    map,
                    zoom:6,
                });
            });
          })
        })
    });
});
    // new google.maps.Marker({
    //   position: { lat: 46.603354, lng: 2.8883335 },
    //   map,
    // });
};