odoo.define('prt_mail_messages_pro.MailNotificationManager', function (require) {
    "use strict";

    var MailNotificationManager = require('mail.Manager.Notification');

    MailNotificationManager.include({

        // Handle notification
        _handlePartnerNotification: function (data) {
            if (data.type === 'move_messages') {
                this._handlePartnerMessagesMove(data);
            } else if (data.type === 'edit_message') {
                this._handlePartnerMessageEdit(data);
            }  else {
                this._super.apply(this, arguments);
            }
        },

        // Move messages
        _handlePartnerMessagesMove: function (data) {
            var self = this;
            // TODO get old_thread_id from data and pass it to moveMessage()
            _.each(data.message_moved_ids, function (movedMessage) {
                var message = self.getMessage(movedMessage[0]);
                if (message) {
                    message.moveMessage(movedMessage[1], movedMessage[2], movedMessage[3], movedMessage[4]);
                }
            });
        },

        // Edit Message
        _handlePartnerMessageEdit: function (data) {
            var mailBus = this.call('mail_service', 'getMailBus');
            var message_id = data.message_id;
            var message = this.getMessage(message_id);

            if (message) {
                this._rpc({
                    model: 'mail.message',
                    method: 'read',
                    args: [[message_id], ['body', 'cx_edit_message']],
                }).then(function (result){
                    var res = result[0];
                    message._body = res.body;
                    message._cx_edit_message = res.cx_edit_message;
                    mailBus.trigger('update_message', message);
                });
            }
        },
    });
});
