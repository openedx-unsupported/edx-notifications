;(function (define) {

define([
    'jquery',
    'backbone',
    'counter_icon_view'
], function($, Backbone, CounterIconView) {
    'use strict';

    return function (config) {
        this.EdxNotificationIcon= new CounterIconView({
            el: $('#edx_notification_counter'),
            pane_el: $('#edx_notification_pane'),
            endpoints: config.endpoints,
            global_variables: config.global_variables,
            view_templates: config.view_templates,
            refresh_watcher: config.refresh_watcher,
            view_audios: config.view_audios
        });
    };

});

})(define || RequireJS.define);
