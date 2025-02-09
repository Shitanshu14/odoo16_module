odoo.define('technians_apps_customization.custom_color_picker', function(require) {
    "use strict";

    var ColorPicker = require('web.color_picker');

    ColorPicker.include({
        init: function() {
            this._super.apply(this, arguments);
            // Customize the palette or other options here
            this.palette = [
                '#FFFFFF', '#000000', '#FF0000', '#00FF00', '#0000FF',
                '#FFFF00', '#FF00FF', '#00FFFF', '#C0C0C0', '#808080',
                '#800000', '#808000', '#008000', '#800080', '#008080', '#000080'
            ];
        }
    });
});
