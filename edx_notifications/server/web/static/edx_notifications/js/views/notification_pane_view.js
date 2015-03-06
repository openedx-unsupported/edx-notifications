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

        this.hydrate();
    },

    events: {
        'click .user_notifications_all': 'allUserNotificationsClicked',
        'click .unread_notifications': 'unreadNotificationsClicked',
        'click .mark_notifications_read': 'markNotificationsRead',
        'click .hide_pane': 'hidePane',
        'click': 'preventHidingWhenClickedInside'
    },

    template: null,

    selected_pane: 'unread',

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

    hydrate: function() {
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
        });
    },

    /* all notification renderer templates */
    renderer_templates: {},

    collectionChanged: function() {
        /* redraw for now */
        this.render();
    },

    render: function() {
        /* if we have data in our collection AND we have loaded */
        /* all of the Notification renderer templates, then let's */
        /* enumerate through all of the notifications we have */
        /* and render each one */

        var grouped_user_notifications = null;
        var grouped_user_notifications = [];

        if (this.selected_pane == 'unread') {
            notification_group_renderings = this.get_notification_group_renderings('type');
        } else {
            notification_group_renderings = this.get_notification_group_renderings('date');
        }

        /* now render template with our model */
        var _html = this.template({
            global_variables: this.global_variables,
            grouped_user_notifications: notification_group_renderings
        });

        this.$el.html(_html);

        // make sure the right tab is highlighted
        this.$el.find($('ul.notifications_list_tab > li')).removeClass('active');
        var class_to_activate = (this.selected_pane == 'unread') ? 'unread_notifications' : 'user_notifications_all';
        this.$el.find('.'+class_to_activate).addClass('active');
    },
    get_notification_group_renderings: function(group_by) {
        var user_msgs = this.collection.toJSON();
        var grouped_data = {};
        var notification_groups = [];
        if (group_by == 'type') {
            // use Underscores built in group by function
            grouped_data = _.groupBy(
                user_msgs,
                function(user_msg) {
                    // group by msg_type name family
                    var name = user_msg.msg.msg_type.name;
                    name = name.substring(0, name.lastIndexOf("."));
                    return name.substring(name.lastIndexOf(".")+1);
                }
            );
        } else {
            // use Underscores built in group by function
            grouped_data = _.groupBy(
                user_msgs,
                function(user_msg) {
                    // group by create date
                    var date = user_msg.msg.created;
                    return new Date(date).toString('MMMM dd, yyyy');
                }
            );
        }

        // Now iterate over the groups and perform
        // a sort by date (desc) inside each msg inside the group and also
        // create a rendering of each message
        for (var group_key in grouped_data) {
            if (grouped_data.hasOwnProperty(group_key)) {
                var notification_group = {
                    group_title: null,
                    messages: []
                };

                // Then within each group we want to sort
                // by create date, descending, so call reverse()
                var sorted_data = _.sortBy(
                    grouped_data[group_key],
                    function(user_msg) {
                        return user_msg.msg.created;
                    }
                ).reverse();

                notification_group['group_title'] = group_key;
                notification_group['messages'] = [];

                // Loop through each msg in the current group
                // and create a rendering of it
                for (var j = 0; j < sorted_data.length; j++) {
                    var user_msg = sorted_data[j];
                    var msg = user_msg.msg;
                    var renderer_class_name = msg.msg_type.renderer;

                    // check to make sure we have the Underscore rendering
                    // template loaded, if not, then skip it.
                    var render_context = jQuery.extend(true, {}, msg.payload);

                    // pass in the selected_view in case the
                    // Underscore templates will how different
                    // renderings depending on which tab is selected
                    render_context['selected_view'] = this.selected_pane;

                    // also pass in the date the notification was created
                    render_context['created'] = msg.created;

                    if (renderer_class_name in this.renderer_templates) {
                        try {
                            var notification_html = this.renderer_templates[renderer_class_name](render_context);

                            notification_group['messages'].push({
                                user_msg: user_msg,
                                msg: msg,
                                /* render the particular NotificationMessage */
                                html: this.renderer_templates[renderer_class_name](render_context)
                            });
                        } catch(err) {
                            console.log('Could not render Notification type ' + msg.msg_type.name + ' with template ' + renderer_class_name + ': ' + err + '. Skipping....')
                        }
                    }
                }

                notification_groups.push(notification_group)
            }
        }

        return notification_groups;
    },
    allUserNotificationsClicked: function(e) {
        // check if the event.currentTarget class has already been active or not
        if (this.selected_pane != 'all') {
            /* set the API endpoint that was passed into our initializer */
            this.collection.url = this.endpoints.user_notifications_all;
            this.selected_pane = 'all';
            this.hydrate();
        }
    },
    unreadNotificationsClicked: function(e) {
        // check if the event.currentTarget class has already been active or not
        if (this.selected_pane != 'unread') {
            /* set the API endpoint that was passed into our initializer */
            this.collection.url = this.endpoints.user_notifications_unread_only;
            this.selected_pane = 'unread';
            this.hydrate();
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
                    self.selected_pane = 'unread';
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
