var NotificationPaneView = Backbone.View.extend({
    initialize: function(options){
        this.global_variables = options.global_variables;
        this.view_templates = options.view_templates;
        this.counter_icon_view = options.counter_icon_view;
        this.namespace = options.namespace;

        var self = this;

        /* get out main underscore view template */
        this.template = _.template($('#notification-pane-template').html());

        // set up our URLs for the API
        this.unread_msgs_endpoint = options.endpoints.user_notifications_unread_only;
        this.all_msgs_endpoint = options.endpoints.user_notifications_all;
        this.mark_all_read_endpoint = options.endpoints.mark_all_user_notifications_read;
        this.mark_notification_read_endpoint = options.endpoints.user_notification_mark_read;

        this.renderer_templates_url_endpoint = options.endpoints.renderer_templates_urls

        /* query endpoints to get a list of all renderer template URLS */
        $.get(this.renderer_templates_url_endpoint).done(function(data){
            self.process_renderer_templates_urls(data);
        });

        // apply namespacing - if set - to our Ajax calls
        if (this.namespace) {
            this.unread_msgs_endpoint = this.append_url_param(this.unread_msgs_endpoint, 'namespace', this.namespace);
            this.all_msgs_endpoint = this.append_url_param(this.all_msgs_endpoint, 'namespace', this.namespace);
        }

        /* set up our collection */
        this.collection = new UserNotificationCollection();

        /* set the API endpoint that was passed into our initializer */
        this.collection.url = this.unread_msgs_endpoint;

        /* re-render if the model changes */
        this.listenTo(this.collection, 'change', this.collectionChanged);

        this.hydrate();
    },

    append_url_param: function(baseUrl, key, value) {
      key = encodeURI(key); value = encodeURIComponent(value);
      var path = baseUrl.split('?')[0]
      var kvp = baseUrl.split('?')[1].split('&');
      var i=kvp.length; var x; while(i--)
      {
          x = kvp[i].split('=');
          if (x[0]==key)
          {
              x[1] = value;
              kvp[i] = x.join('=');
              break;
          }
      }
      if(i<0) {kvp[kvp.length] = [key,value].join('=');}
      return path + '?' + kvp.join('&');
    },

    events: {
        'click .user_notifications_all': 'allUserNotificationsClicked',
        'click .unread_notifications': 'unreadNotificationsClicked',
        'click .mark_notifications_read': 'markNotificationsRead',
        'click .hide_pane': 'hidePane',
        'click .edx-notifications-content>ul>li': 'visitNotification',
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
                                html: notification_html
                            });
                        } catch(err) {
                            console.log('Could not render Notification type ' + msg.msg_type.name + ' with template ' + renderer_class_name + '. Error: "' + err + '". Skipping....')
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
            this.collection.url = this.all_msgs_endpoint;
            this.selected_pane = 'all';
            this.hydrate();
        }
    },
    unreadNotificationsClicked: function(e) {
        // check if the event.currentTarget class has already been active or not
        /* set the API endpoint that was passed into our initializer */
        this.collection.url = this.unread_msgs_endpoint;
        this.selected_pane = 'unread';
        this.hydrate();
    },
    markNotificationsRead: function(e) {
        /* set the API endpoint that was passed into our initializer */
        this.collection.url = this.mark_all_read_endpoint;

        /* make the async call to the backend REST API */
        /* after it loads, the listenTo event will file and */
        /* will call into the rendering */
        var self = this;
        self.$el.addClass('ui-loading');
        var data = {}
        if (this.namespace) {
            data = {
                namespace: this.namespace
            }
        }
        self.collection.fetch(
            {
                headers: {
                    "X-CSRFToken": this.getCSRFToken()
                },
                type: 'POST',
                data: data,
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
    getCSRFToken: function() {
        var cookieValue = null;
        var name='csrftoken';
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },
    visitNotification: function(e) {
        var messageId = $(e.currentTarget).find('span').data('msg-id');
        var clickLink = $(e.currentTarget).find('span').data('click-link');

        if (this.selected_pane === "unread") {
            this.collection.url = this.mark_notification_read_endpoint + messageId;

            var self = this;
            self.collection.fetch(
                {
                    headers: {
                        "X-CSRFToken": this.getCSRFToken()
                    },
                    data: {
                      "mark_as": "read"
                    },
                    type: 'POST',
                    success: function () {
                        if (clickLink) {
                            window.location.href = clickLink;
                        }
                        else {
                            self.unreadNotificationsClicked();
                            // fetch the latest notification count
                            self.counter_icon_view.model.fetch();
                        }
                    }
                }
            );
        }
        else if (clickLink){
            window.location.href = clickLink;
        }
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
