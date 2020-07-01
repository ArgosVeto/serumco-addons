/* Copyright 2018 Jose ANDRIANANTOAVINA <joseandrianatoavina@gmail.com>
             2018 Harifetra RAKOTOMALALA for v.11
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

odoo.define('web_widget_binary_filter.file_filter', function (require) {
    'use strict';

    var registry = require('web.field_registry'),
        core = require('web.core'),
        AbstractField = require('web.AbstractField');
    var _translate = core._t;
    var FieldBinaryFile = registry.get('binary');
    var FieldBinaryFileFilter = FieldBinaryFile.extend({
        className: 'o_field_binary_file',

        init: function(){
            this._super.apply(this, arguments);
        },

         _renderEdit: function(){
            this._super.apply(this, arguments);
            if (this.nodeOptions.accept && this.nodeOptions.accept.length > 0){
                var input_file = this.$("input[name=ufile]");
                input_file.attr("accept", this.nodeOptions.accept);
            };
         },

        on_file_change: function(e) {
            if (this.nodeOptions.accept && this.nodeOptions.accept.length > 0){
                var valid_file_extensions = this.nodeOptions.accept.split(',');
                var file_node = e.target;
                var file = file_node.files[0];
                var file_name = file.name;
                var ext = file_name.split('.').pop();
                if ($.inArray('.'+ext, valid_file_extensions) == -1){
                    var msg = _translate("Invalid file extension! Allowed extensions:") + (valid_file_extensions.join(", ")).toUpperCase();
                    this.do_warn(_translate("File upload"), msg);
                    return false;
                };
            };
            this._super.apply(this, arguments);
         },
    });

    registry.add('file_filter', FieldBinaryFileFilter);
});
