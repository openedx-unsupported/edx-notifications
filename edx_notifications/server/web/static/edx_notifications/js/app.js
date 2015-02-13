;(function (define) {

define([
    'jquery',
    'backbone',
    '/static/edx_notifications/js/views/counter_icon_view.js',
], function($, Backbone, CounterIconView) {
    'use strict';

    return function (config) {
        this.EdxNotificationIcon= new CounterIconView({
            el: $('#edx_notification_counter'),
            pane_el: $('#edx_notification_pane'),
            endpoints: config.endpoints,
            view_templates: config.view_templates
        });
    };

});

})(define || RequireJS.define);
