var tests = [];
for (var file in window.__karma__.files) {
    if (/Spec\.js$/.test(file)) {
        tests.push(file);
    }
}

requirejs.config({
    // Karma serves files from '/base'
    baseUrl: '/base/edx_notifications/server/web/',

    paths: {
        'jquery': 'static/edx_notifications/js/vendor/dev/jquery',
        'underscore': 'static/edx_notifications/js/vendor/dev/underscore',
        'backbone': 'static/edx_notifications/js/vendor/dev/backbone',
        'text': 'static/edx_notifications/js/vendor/dev/text',
        'counter_icon_view' : 'static/edx_notifications/js/views/counter_icon_view',
        'counter_icon_model': 'static/edx_notifications/js/models/counter_icon_model',
        'notification_pane_view': 'static/edx_notifications/js/views/notification_pane_view',
        'notification_icon_template': 'static/edx_notifications/templates/notification_icon.html',
        'notification_collection': 'static/edx_notifications/js/collections/notification_collection',
        'notification_pane_template': 'static/edx_notifications/templates/notification_pane.html',
        'user_notification_model': 'static/edx_notifications/js/models/user_notification_model'
    },

    shim: {
        'underscore': {
            exports: '_'
        }
    },

    // ask Require.js to load these files (all our tests)
    deps: tests,

    // start test run, once Require.js is done
    callback: window.__karma__.start
});
