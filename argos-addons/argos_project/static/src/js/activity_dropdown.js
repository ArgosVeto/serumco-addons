odoo.define('argos_project.activity', function (require) {
    "use strict";

    var core = require('web.core')
    var ajax = require('web.ajax');
    var qweb = core.qweb

    ajax.loadXML('/argos_project/static/src/xml/activity_dropdown.xml', qweb);
});