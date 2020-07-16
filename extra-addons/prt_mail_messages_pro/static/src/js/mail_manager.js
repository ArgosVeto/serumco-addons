odoo.define('prt_mail_messages_pro.MailManager', function (require) {
    "use strict";

    var MailManager = require('mail.Manager');

    MailManager.include({

        // Remove from threads
        removeMessageFromThreads: function (message) {
            var self = this;
            var message_id = message.getID();
            _.each(message.getThreadIDs(), function (threadID) {
                var thread = self.getThread(threadID);
                if (thread && thread._type) {
                    // Count non document threads
                    if (thread._type === 'document_thread') {
                        thread._messageIDs = _.reject(thread._messageIDs, function (id) {
                            return id === message_id;
                        });
                        thread._messages = _.reject(thread._messages, function (msg) {
                            return msg._id === message_id;
                        });
                        // Update list of deleted messages
                        var deletedMessageIDs = thread.deletedMessageIDs || true;
                        thread.deletedMessageIDs = deletedMessageIDs;
                    } else {
                        thread.removeMessage(message_id);
                    }
                }
            });
        },
    });
});
