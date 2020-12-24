odoo.define('website_argos.portal_chatter', function (require) {
'use strict';

var portalChatter = require('portal.chatter');
var core = require('web.core');
var _t = core._t;
var utils = require('web.utils');
var time = require('web.time');
var _t = core._t;
var PortalChatter = portalChatter.PortalChatter;
var qweb = core.qweb;

PortalChatter.include({
	preprocessMessages: function (messages) {
        _.each(messages, function (m) {
            m['author_avatar_url'] = _.str.sprintf('/web/image/%s/%s/author_avatar/50x50', 'mail.message', m.id);
            m['published_date_str'] = _.str.sprintf(_t('Le %s'), moment(time.str_to_datetime(m.date)).format('DD/MM/YYYY'));
        });
        return messages;
    },
	})
})