var NotificationPaneView = Backbone.View.extend({
    initialize: function(options){
        this.endpoints = options.endpoints;

        var self = this;
        /* get out main backbone view template */
        $.get("/static/edx_notifications/templates/underscore/notification_pane.html")
            .done(function(template_data) {
        /* convert to Underscore template object */
                self.fetched_template = _.template(template_data);
                self.render();
            });

        /* query endpoints to get a list of all renderer template URLS */
        $.get(this.endpoints.renderer_templates_urls).done(function(data){
            self.process_renderer_templates_urls(data);
        });

        /* set up our collection */
        this.collection = new UserNotificationCollection();

        /* set the API endpoint that was passed into our initializer */
        this.collection.url = this.endpoints.user_notifications

        /* re-render if the model changes */
        this.listenTo(this.collection, 'change', this.collectionChanged);

        this.hydrate();

        this.render();
    },

    process_renderer_templates_urls: function(data) {
        /*
        This will go through all Underscore Notification Renderer Templates
        that have been registered with the system and load them
        */
        var self = this;

        var number_to_fetch = 0
        for (var renderer_class in data) {
            if (data.hasOwnProperty(renderer_class)) {
                number_to_fetch++;
            }
        }

        var renderer_templates = {};

        for (var renderer_class in data) {
            if (data.hasOwnProperty(renderer_class)) {
                var url = data[renderer_class];
                $.get(url).done(function(template_data) {
                    number_to_fetch--;
                    renderer_templates[renderer_class] = _.template(template_data);
                    if (number_to_fetch == 0) {
                        self.renderer_templates = renderer_templates;
                        self.render();
                    }
                });
            }
        }
    },

    hydrate: function() {
        /* This function will load the bound collection */

        /* add and remove a class when we do the initial loading */
        /* we might - at some point - add a visual element to the */
        /* loading, like a spinner */
        var self = this;
        self.$el.addClass('ui-loading');
        this.collection.fetch({
            success: function(){
                self.$el.removeClass('ui-loading')
                self.render();
            }
        });
    },

    /* cached notification_icon.html template */
    fetched_template: null,

    /* all notification renderer templates */
    renderer_templates: null,

    collectionChanged: function() {
        /* redraw for now */
        this.render();
    },

    render: function() {
        /* if we have data in our collection AND we have loaded */
        /* all of the Notification renderer templates, then let's */
        /* enumerate through all of the notifications we have */
        /* and render each one */

        if (this.fetched_template !== null) {
            var user_notifications =[]
            if (this.collection !== null && this.renderer_templates !== null) {
                for (var i=0; i<this.collection.length; i++) {
                    var user_msg = this.collection.at(i);
                    var msg = user_msg.get("msg");
                    var msg_type = msg.msg_type;
                    var renderer_class_name = msg_type.renderer;
                    user_notifications.push({
                        user_msg: user_msg,
                        html: this.renderer_templates[renderer_class_name](msg.payload),
                    });
                }
            }

            /* now render template with our model */
            this.$el.html(
                this.fetched_template({
                    user_notifications: user_notifications
                })
            );
        }
    }
});
