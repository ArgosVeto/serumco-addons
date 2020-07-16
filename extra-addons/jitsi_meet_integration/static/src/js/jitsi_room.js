odoo.define('jitsi_meet_integration.JitsiRoom', function (require) {
    "use strict";

    require('web.dom_ready');

    // Example to load and attach a widget
    var root = $('#wrap');
    if (root.length === 0) {
        return;
    }
    if ($(root).data('jitsi') !== 1) {
        return;
    }
    var JitsiRoomWidget = require('jitsi_meet_integration.JitsiRoomWidget');

    var jitsiRoom = new JitsiRoomWidget();
    jitsiRoom.appendTo(root);

});        