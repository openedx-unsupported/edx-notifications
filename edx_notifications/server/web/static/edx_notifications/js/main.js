
/* define a base requirejs configuration. Note applications can add override paths */
var _edxnotifications_requirejs_config = {
  paths: {
    jquery: '/static/js/vendor/jquery',
    backbone: '/static/js/vendor/backbone',
    underscore: '/static/js/vendor/underscore',
    text: '/static/js/vendor/text',
    date: '/static/js/vendor/date',
    notifications_app: '/static/edx_notifications/js/app',
    counter_icon_view: '/static/edx_notifications/js/views/counter_icon_view',
    counter_icon_model: '/static/edx_notifications/js/models/counter_icon_model',
    notification_pane_view: '/static/edx_notifications/js/views/notification_pane_view',
    notification_collection: '/static/edx_notifications/js/collections/notification_collection',
    user_notification_model: '/static/edx_notifications/js/models/user_notification_model',
    notification_pane_template: '/static/edx_notifications/templates/notification_pane.html',
    notification_icon_template: '/static/edx_notifications/templates/notification_icon.html'
  },
  shim: {
    "backbone": {
      deps: ["underscore", "jquery"],
      exports: "Backbone"
    }
  }
};

if (typeof _edxnotifications_requirejs_path_overrides !== 'undefined') {
    for (var attrname in _edxnotifications_requirejs_path_overrides)
        {
            _edxnotifications_requirejs_config.paths[attrname] = _edxnotifications_requirejs_path_overrides[attrname];
        }
}

require.config(_edxnotifications_requirejs_config);


require([
    'jquery',
    'notifications_app',
], function($, NotificationsApp) {

    if (typeof edxnotificationsAppConfiguration !== 'undefined') {
        this.app = new NotificationsApp(edxnotificationsAppConfiguration);
    }

});
