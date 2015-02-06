var CounterIconModel = Backbone.Model.extend({
    /* model for the Notification Icon which will display a counter of unread messages */

    defaults: {
        'count': null
    },

    /* API endpoint */
    url: "/api/edx_notifications/v1/consumer/notifications/count/"
});
