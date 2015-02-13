;(function (define) {

define([
    'backbone',
    '/static/edx_notifications/js/models/user_notification_model.js',
], function (Backbone, UserNotificationModel) {
    'use strict';

    return Backbone.Collection.extend({
        /* model for a collection of UserNotifications */
        model: UserNotificationModel,

    });
});
})(define || RequireJS.define);
