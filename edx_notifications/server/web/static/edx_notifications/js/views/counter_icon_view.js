var CounterIconView = Backbone.View.extend({
    initialize: function(options){
        this.options = options;

        /* re-render if the model changes */
        this.listenTo(this.model,'change', this.render);

        /* make the async call to the backend REST API */
        this.model.fetch();

        /* do initial rendering before model is fetched */
        this.render();
    },

    events: {
        'click .edx-notifications-icon': 'showPane'
    },

    /* cached notification_icon.html template */
    fetched_template: null,

    /* cached notifications pane view */
    notification_pane: null,

    render: function () {
        if (!this.fetched_template) {
            var self = this;

            /* load Underscore template asynchronously on first load */
            $.get("/static/edx_notifications/templates/underscore/notification_icon.html")
                .done(function(template_data) {

                    /* convert to Underscore template object */
                    self.fetched_template = _.template(template_data);

                    /* now render template with our model */
                    self.$el.html(
                        self.fetched_template(
                            self.model.toJSON()
                        )
                    );
            });
        } else {
            /* we already have the Underscore template, so just render it with out model */
            self.$el.html(
                self.fetched_template(
                    self.model.toJSON()
                )
            );
        }
   },

   showPane: function() {
        if (!this.notification_pane) {
            this.notification_pane = new NotificationPaneView({
                el: this.options.pane_el,
                collection: new UserNotificationCollection()
            });
        } else {
            this.notification_pane.show();
        }
   }
});
