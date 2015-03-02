;(function (define) {

define([
    'jquery',
    'backbone',
    'counter_icon_model',
    'notification_pane_view',
    'text!notification_icon_template'
], function (
    $, Backbone, CounterIconModel, NotificationPaneView, NotifcationIconUnderscoreTemplate
) {
    'use strict';

    return Backbone.View.extend({
        initialize: function(options){
            this.options = options;
            this.endpoints = options.endpoints;
            this.global_variables = options.global_variables;
            this.view_templates = options.view_templates;
            this.refresh_watcher = options.refresh_watcher;
            this.view_audios = options.view_audios;

            /* initialize the model using the API endpoint URL that was passed into us */
            this.model = new CounterIconModel();
            this.model.url = this.endpoints.unread_notification_count;

            /* re-render if the model changes */
            this.listenTo(this.model,'change', this.modelChanged);

            /* make the async call to the backend REST API */
            /* after it loads, the listenTo event will file and */
            /* will call into the rendering */
            this.model.fetch();

            /* adding short-poll capabilities to refresh notification counter */
            if(this.refresh_watcher.name == 'short-poll'){
                var period = this.refresh_watcher.args.poll_period_secs;
                setInterval(this.autoRefreshNotifications.bind(window, this), period * 1000);
            }
        },

        events: {
            'click .edx-notifications-icon': 'showPane',
            'click this.options' : 'hidePane'
        },

        /* cached notifications pane view */
        notification_pane: null,

        /* cached user_notifications_mark_true view */
        user_notifications_mark_true: null,

        template: null,

        modelChanged: function() {
            this.render();
        },

        render: function () {

            if (!this.template)
                this.template = _.template(NotifcationIconUnderscoreTemplate);

            this.$el.html(this.template(
                    this.model.toJSON()
                )
            );
       },

       showPane: function() {
            if (!this.notification_pane) {

                this.notification_pane = new NotificationPaneView({
                    counter_icon_view: this,
                    el: this.options.pane_el,
                    endpoints: this.endpoints,
                    global_variables: this.global_variables,
                    view_templates: this.view_templates
                });

            }
           else {
                this.notification_pane.showPane();
           }
        },

        autoRefreshNotifications: function(counterView) {
           var currentModel = new CounterIconModel();
           currentModel.url = counterView.endpoints.unread_notification_count;
           currentModel.fetch().done(function(){
               // if notification counter is incremented.
               if(currentModel.get('count') > counterView.model.get('count')){
                   var notification_alert = new Audio(counterView.view_audios.notification_alert);
                   counterView.model = currentModel;
                   notification_alert.play();
                   counterView.render();
                   if (counterView.notification_pane) {
                       counterView.notification_pane.hydrate();
                   }
               }
           });
       }
    });
});
})(define || RequireJS.define);
