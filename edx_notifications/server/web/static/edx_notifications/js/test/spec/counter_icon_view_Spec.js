describe("CounterIconView", function(){

    beforeEach(function(){
        this.server = sinon.fakeServer.create();
        setFixtures(
            '<div><img class="edx-notifications-icon" src="/static/edx_notifications/img/notification_icon.jpg" />' +
            '<span class="edx-notifications-count-number"></span> </div>' +
            '<div class="edx-notification-pane">' +
            '<script type="text/template" id="notification-counter-template">' +
                '<% if (typeof count !== "undefined" && count > 0) { %>' +
                '<%= count %><% } %>' +
            '</script>'
        );
        this.counter_view = new CounterIconView({
            el: $(".edx-notifications-icon"),
            count_el: $(".edx-notifications-count-number"),
            pane_el: $(".edx-notification-pane"),
            endpoints: {
                unread_notification_count: "/unread/count/?read=False&unread=True",
                mark_all_user_notifications_read: "mark/as/read",
                user_notifications_all:"all/notifications/?read=True&unread=True",
                user_notifications_unread_only: "unread/notifications/?read=False&unread=True",
                renderer_templates_urls: "/renderer/templates"
            },
            global_variables: {
                app_name: "mcka"
            },
            refresh_watcher: {
                name: "none",
                args: "refresh"
            },
            view_audios: {
                notification_alert: "chirp"
            },

            namespace: "/foo/bar/baz"
        });
        this.counter_view.render();
    });

    afterEach(function() {
        this.server.restore();
    });

    it("assigns value to namespace", function(){
        expect(this.counter_view.namespace).toBe('/foo/bar/baz')
    });

    it("assigns value to audio", function(){
        expect(this.counter_view.view_audios.notification_alert).toBe('chirp')
    });

    it("assigns value to global variables", function(){
        expect(this.counter_view.global_variables.app_name).toBe('mcka')
    });

    it("assigns value to refresh watchers", function(){
        expect(this.counter_view.refresh_watcher.args).toBe('refresh')
    });


    it("assigns unread notifications count url as model url", function(){
        expect(this.counter_view.model.url).toBe('/unread/count/?read=False&unread=True&namespace=%2Ffoo%2Fbar%2Fbaz')
    });

    it("checks if emplate function is defined", function(){
        expect(this.counter_view.template).toBeDefined()
    });

    it("returns unread_notification_count url in endpoint", function(){
        expect(this.counter_view.endpoints.unread_notification_count).toEqual('/unread/count/?read=False&unread=True');
    });

    it("returns mark_all_user_notifications_read url in endpoint", function(){
        expect(this.counter_view.endpoints.mark_all_user_notifications_read).toEqual('mark/as/read');
    });

    it("returns all_notifications url in endpoint", function(){
        expect(this.counter_view.endpoints.user_notifications_all).toBe('all/notifications/?read=True&unread=True');
    });

    it("returns unread_notifications url in endpoint", function(){
        expect(this.counter_view.endpoints.user_notifications_unread_only).toContain('unread/notifications/');
    });

    it("returns renderer_templates_urls in endpoints", function(){
        expect(this.counter_view.endpoints.renderer_templates_urls).toEqual('/renderer/templates');
    });

    it("returns notification icon class in el", function(){
        expect(this.counter_view.$el).toContain('.edx-notifications-icon')
    });


    it("calls showPane function on clicking notification icon", function(){
        var target = $(".edx-notifications-icon");
        var showPaneSpy = spyOn(this.counter_view, 'showPane');
        this.counter_view.delegateEvents();
        target.click();
        expect(showPaneSpy).toHaveBeenCalled();
    });

});