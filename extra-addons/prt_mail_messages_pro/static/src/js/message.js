odoo.define('prt_mail_messages_pro.Message', function (require) {
    "use strict";

    var Message = require('mail.model.Message');

    Message.include({

        // Set initial data
        _setInitialData: function (data){
            this._super.apply(this, arguments);
            this._cx_edit_message = data.cx_edit_message;
        },

        // Move message
        moveMessage: function (oldThreadID, newThreadID, oldRecData, newRecData) {
            var mailBus = this.call('mail_service', 'getMailBus');
            var oldThread = this.call('mail_service', 'getThread', oldThreadID);
            var message_id = this._id;

            // Remove message from old thread
            if (oldThread) {
                oldThread._messageIDs = _.reject(oldThread._messageIDs, function (id) {
                    return id === message_id;
                });
                oldThread._messages = _.reject(oldThread._messages, function (msg) {
                    return msg._id === message_id;
                });
            }

            // Add message to new thread
            var newThread = this.call('mail_service', 'getThread', newThreadID);

            if (newThread) {
                this._documentModel = newRecData[0];
                this._documentID = newRecData[1];
                this._threadIDs.push(newThreadID);
                newThread._messageIDs.push(message_id);
                newThread._messages.push(this);
            }

            mailBus.trigger('update_message', this);

            // Remove old thread if from message
            this._threadIDs = _.reject(this._threadIDs, function (thread) {
                return thread === oldThreadID;
            });
        },
    });
});
