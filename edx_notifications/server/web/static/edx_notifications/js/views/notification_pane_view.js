var NotificationPaneView = Backbone.View.extend({
    initialize: function(options){

        /* set up our collection */
        this.collection = new UserNotificationCollection();

        /* set the API endpoint that was passed into our initializer */
        this.collection.url = options.user_notifications_endpoint;

        /* re-render if the model changes */
        this.listenTo(this.collection, 'change', this.collectionChanged);

        this.hydrate();

        this.render();
    },

    hydrate: function() {
        /* This function will load the bound collection */

        /* add and remove a class when we do the initial loading */
        /* we might - at some point - add a visual element to the */
        /* loading, like a spinner */
        var self = this;
        self.$el.addClass('loading');
        this.collection.fetch({
            success: function(){
                self.$el.removeClass('loading')
            }
        });
    },

    /* cached notification_icon.html template */
    fetched_template: null,

    collectionChanged: function() {
        /* redraw for now */
        this.render();
    },

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
