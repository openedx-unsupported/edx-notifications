var CounterIconModel = Backbone.Model.extend({
    /* model for the Notification Icon which will display a counter of unread messages */

    defaults: {
        /* start with unknown number of unread notifications */
        'count': null
    },

    /* REST API endpoint to use to get authenticated user's notification count */
    url: "/api/edx_notifications/v1/consumer/notifications/count?unread=True&read=False"
});
