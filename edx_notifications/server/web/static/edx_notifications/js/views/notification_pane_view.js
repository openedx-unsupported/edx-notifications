var NotificationPaneView = Backbone.View.extend({
    initialize: function(options){
        this.endpoints = options.endpoints;
        this.global_variables = options.global_variables;
        this.view_templates = options.view_templates;
        this.counter_icon_view = options.counter_icon_view;

        var self = this;

        /* get out main underscore view template */
        this.template = _.template($('#notification-pane-template').html());

        /* query endpoints to get a list of all renderer template URLS */
        $.get(this.endpoints.renderer_templates_urls).done(function(data){
            self.process_renderer_templates_urls(data);
        });

        /* set up our collection */
        this.collection = new UserNotificationCollection();

        /* set the API endpoint that was passed into our initializer */
        this.collection.url = this.endpoints.user_notifications_unread_only;

        /* re-render if the model changes */
        this.listenTo(this.collection, 'change', this.collectionChanged);

        this.hydrate('unread_notifications');

        this.render();
    },

    events: {
        'click .user_notifications_all': 'allUserNotificationsClicked',
        'click .unread_notifications': 'unreadNotificationsClicked',
        'click .mark_notifications_read': 'markNotificationsRead',
        'click .hide_pane': 'hidePane',
        'click': 'preventHidingWhenClickedInside'
    },

    template: null,

    selected_pane: 'unread_notifications',

    process_renderer_templates_urls: function(data) {
        /*
        This will go through all Underscore Notification Renderer Templates
        that have been registered with the system and load them
        */
        var self = this;

        var number_to_fetch = 0;
        for (var item in data) {
            if (data.hasOwnProperty(item)) {
                number_to_fetch++;
            }
        }

        var renderer_templates = {};

        for (var renderer_class in data) {
            if (data.hasOwnProperty(renderer_class)) {
                var url = data[renderer_class];
                $.ajax({url: url, context: renderer_class}).done(function(template_data) {
                    number_to_fetch--;
                    renderer_templates[this] = _.template(template_data);
                    if (number_to_fetch === 0) {
                        /* when we've loaded them all, then call render() again */
                        self.renderer_templates = renderer_templates;
                        self.render();
                    }
                });
            }
        }
    },

    hydrate: function(selected_tab_classname) {
        /* This function will load the bound collection */

        /* add and remove a class when we do the initial loading */
        /* we might - at some point - add a visual element to the */
        /* loading, like a spinner */
        var self = this;
        self.$el.addClass('ui-loading');
        this.collection.fetch({
            success: function(){
                self.$el.removeClass('ui-loading');
                self.render();
            }
        }).done(function(){
            if (selected_tab_classname) {
                self.$el.find($('ul.notifications_list_tab > li')).removeClass('active');
                self.$el.find('.'+selected_tab_classname).addClass('active');
            }
        });
    },

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
            var grouped_user_notifications = [];

            if (this.selected_pane == 'unread_notifications') {
                this.get_grouped_notifications(grouped_user_notifications, 'type');
            } else {
                this.get_grouped_notifications(grouped_user_notifications, 'date');
            }

            /* now render template with our model */
            var _html = this.template({
                global_variables: this.global_variables,
                grouped_user_notifications: grouped_user_notifications
            });

            this.$el.html(_html);
        }
    },
    get_grouped_notifications: function(grouped_user_notifications, group_by){
        var current_group_type = null;
        var notification_group = {};
        var old_group_type = '';
        if (this.collection !== null && this.renderer_templates !== null) {
            for (var i = 0; i < this.collection.length; i++) {
                var user_msg = this.collection.at(i);
                var msg = user_msg.get("msg");
                var msg_type = msg.msg_type;
                var renderer_class_name = msg_type.renderer;
                if (group_by === 'type') {
                    current_group_type = msg_type.name.substring(0, msg_type.name.lastIndexOf("."));
                    current_group_type = current_group_type.substring(current_group_type.lastIndexOf(".") + 1);
                }
                else if (group_by === 'date') {
                    current_group_type = new Date(msg.created).toString('MMMM dd, yyyy');
                }
                if (old_group_type !== current_group_type) {
                    if (old_group_type) {
                        grouped_user_notifications.push(notification_group);
                    }
                    notification_group = {};

                    notification_group['group_title'] = current_group_type;
                    notification_group['messages'] = [];
                    old_group_type = current_group_type;
                }
                notification_group['messages'].push({
                    user_msg: user_msg,
                    msg: msg,
                    /* render the particular NotificationMessage */
                    html: this.renderer_templates[renderer_class_name](msg.payload)
                });
            }
            if (!$.isEmptyObject(notification_group)) {
                grouped_user_notifications.push(notification_group);
            }
        }
    },
    allUserNotificationsClicked: function(e) {
        // check if the event.currentTarget class has already been active or not
        if (this.selected_pane != 'user_notifications_all') {
            /* set the API endpoint that was passed into our initializer */
            this.collection.url = this.endpoints.user_notifications_all;
            this.selected_pane = 'user_notifications_all';
            this.hydrate(this.selected_pane);
        }
    },
    unreadNotificationsClicked: function(e) {
        // check if the event.currentTarget class has already been active or not
        if (this.selected_pane = 'unread_notifications') {
            /* set the API endpoint that was passed into our initializer */
            this.collection.url = this.endpoints.user_notifications_unread_only;
            this.selected_pane = 'unread_notifications';
            this.hydrate(this.selected_pane);
        }
    },
    markNotificationsRead: function(e) {
        /* set the API endpoint that was passed into our initializer */
        this.collection.url = this.endpoints.mark_all_user_notifications_read;

        /* make the async call to the backend REST API */
        /* after it loads, the listenTo event will file and */
        /* will call into the rendering */
        var self = this;
        self.$el.addClass('ui-loading');
        self.collection.fetch(
            {
                headers: {
                    "X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').prop('value')
                },
                type: 'POST',
                success: function () {
                    self.$el.removeClass('ui-loading');
                    self.selected_pane = 'unread_notifications';
                    self.render();

                    // fetch the latest notification count
                    self.counter_icon_view.model.fetch();
                }
            }
        );
    },
    hidePane: function() {
        this.$el.hide();
    },
    showPane: function() {
        this.$el.show();
    },
    preventHidingWhenClickedInside: function(e) {
      e.stopPropagation();
    },
    isVisible: function() {
      if ($('.edx-notifications-container').is(':visible')) {
        return true;
      }
      else {
        return false;
      }
    }
});
