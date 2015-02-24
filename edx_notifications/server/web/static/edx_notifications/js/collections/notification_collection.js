;(function (define) {

define([
    'backbone',
    'user_notification_model'
], function (Backbone, UserNotificationModel) {
    'use strict';

    return Backbone.Collection.extend({
        /* model for a collection of UserNotifications */
        model: UserNotificationModel

    });
});
})(define || RequireJS.define);
