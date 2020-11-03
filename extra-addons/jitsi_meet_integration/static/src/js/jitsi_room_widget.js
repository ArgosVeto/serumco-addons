odoo.define('jitsi_meet_integration.JitsiRoomWidget', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var _t = core._t;

    require('web.dom_ready');

    var JitsiRoomWidget = Widget.extend({
        template: 'jitsi_meet_integration.room_content',
        xmlDependencies: ['/jitsi_meet_integration/static/src/xml/templates.xml'],
        event_id: 0,
        init: function () {
            var self = this;
            var res = this._super();
            var wrapElement = $('#wrap');
            self.jitsi_server = wrapElement.data('server');
            self.event_id = wrapElement.data('eventid');
            self.attendee_id = wrapElement.data('attendeeid');
            self.publicAccess = wrapElement.data('public') == 1;
            self.eventId = self.event_id;
            self.autostart = wrapElement.data('autostart');
            self.room = wrapElement.data('room');
            self.company = wrapElement.data('company');
            self.subject = wrapElement.data('subject');
            self.userName = wrapElement.data('name');
            self.password = wrapElement.data('password');
            self.email = wrapElement.data('email');
            return res;
        },

        start: function () {
            var self = this;
            if (!self.autostart) {
                return;
            }

            self.api = new JitsiMeetExternalAPI(self.jitsi_server, {
                roomName: self.room,
                height: $(window).height() - $('header').height() - $('footer').height(),
                parentNode: document.querySelector('#jitsi_meet_content'),
                interfaceConfigOverwrite: {},
            });

            self.api.executeCommand('subject', self.subject);
            self.api.executeCommand('email', self.email);
            self.api.executeCommand('displayName', self.userName);

            if (!self.publicAccess) {
                self.api.on('videoConferenceJoined', function () {
                    if (self.password) {
                        self.api.executeCommand('password', self.password);
                    }
                    rpc.query({
                        route: "/jitsi/rpc/open",
                        params: {
                            event_id: self.eventId
                        }
                    }).then(function (res) {
                        if (!res) {
                            alert('Could not open the Meeting!!!');
                        } else {
                            self.$el.find('.js-jitsi-ready').slideDown(500).delay(5000).slideUp(500);
                        }
                    });
                });
            }

            self.api.on('readyToClose', function () {
                self.api.dispose();
                self.$el.html(core.qweb.render('jitsi_meet_integration.room_closed', {
                    event_id: self.eventId,
                    attendee_id: self.attendee_id,
                    public: self.publicAccess,
                }));
            });
        },
    });

    return JitsiRoomWidget;

});        