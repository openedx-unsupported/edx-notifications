var CounterIconView = Backbone.View.extend({
    initialize: function(){
        /* re-render if the model changes */
        this.listenTo(this.model,'change', this.render);

        /* make the async call to the backend REST API */
        this.model.fetch();

        /* do initial rendering before model is fetched */
        this.render();
    },

    fetched_template: null,

    render: function () {
        if (!this.fetched_template) {
            var self = this;
            $.get("/static/edx_notifications/templates/underscore/notification_icon.html")
                .done(function(template_data) {
                    self.fetched_template = _.template(template_data);
                    self.$el.html(self.fetched_template(self.model.toJSON()))
            });
        } else {
            self.$el.html(self.fetched_template(self.model.toJSON()))
        }
   }
});
