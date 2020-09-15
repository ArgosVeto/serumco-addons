odoo.define('search_more_shorcut.search_more_shorcut', function (require) {
    "use strict";
    var FieldMany2One = require('web.relational_fields').FieldMany2One;
    var proto = $.ui.autocomplete.prototype;
    FieldMany2One.include({
        _manageSearchMore: function (values, search_val, domain, context) {
            var res = this._super.apply(this, arguments);
            if (res.length > this.limit) {
                var search_more_item = res[this.limit];
                search_more_item.is_search_more = true;
            }
            return res;
        }
    });

    $.extend(proto, {
        _renderItem: function (ul, item) {
            if (item.is_search_more) {
                return $("<li></li>")
                    .data("item.autocomplete", item)
                    .append($("<a accesskey='F' aria-keyshortcuts=\"Alt+shift+F\"></a>")[this.options.html ? "html" : "text"](item.label))
                    .appendTo(ul)
                    .addClass(item.classname);
            }
            return $("<li></li>")
                .data("item.autocomplete", item)
                .append($("<a></a>")[this.options.html ? "html" : "text"](item.label))
                .appendTo(ul)
                .addClass(item.classname);
        },
    });
});