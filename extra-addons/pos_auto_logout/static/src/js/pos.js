odoo.define('pos_auto_logout', function(require) {
    "use strict";

    var chrome = require('point_of_sale.chrome');
    var core = require('web.core');
    var _t = core._t;

    chrome.Chrome.include({
        build_widgets:function() {
            var self = this;
            this._super();
            if(self.pos.config.allow_auto_logout){
                var timeout = setTimeout(function() {
                    self.return_to_login_screen();
                }, self.pos.config.logout_time *1000);
                $(document).on('mousemove', function() {
                    if (timeout !== null) {
                        clearTimeout(timeout);
                    }
                    timeout = setTimeout(function() {
                        self.return_to_login_screen();
                    }, self.pos.config.logout_time *1000);
                });
            }
        },
    });
});
