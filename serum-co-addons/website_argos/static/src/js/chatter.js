odoo.define('website_argos.message_thread', function (require) {
'use strict';

var portalChatter = require('portal.chatter');

portalChatter.PortalChatter.include({
    xmlDependencies: (portalChatter.PortalChatter.prototype.xmlDependencies || [])
        .concat(['/website_argos/static/src/xml/portal_chatter.xml']),
});
});
