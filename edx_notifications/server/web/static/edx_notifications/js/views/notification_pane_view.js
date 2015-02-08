var NotificationPaneView = Backbone.View.extend({
    initialize: function(){
        /* re-render if the model changes */
        this.listenTo(this.collection, 'change', this.render);

        this.collection.fetch();

        this.render();
    },

    /* cached notification_icon.html template */
    fetched_template: null,

    render: function() {
        if (!this.fetched_template) {
            var self = this;

            /* load Underscore template asynchronously on first load */
            $.get("/static/edx_notifications/templates/underscore/notification_pane.html")
                .done(function(template_data) {

                    /* convert to Underscore template object */
                    self.fetched_template = _.template(template_data);

                    /* now render template with our model */
                    self.$el.html(
                        self.fetched_template(
                            self.collection.toJSON()
                        )
                    );
            });
        }
    }
});
