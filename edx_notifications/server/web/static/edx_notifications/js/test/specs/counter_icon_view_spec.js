describe("CounterIconView", function(){

    beforeEach(function(){
        this.server = sinon.fakeServer.create();
        setFixtures('<div id="edx_notification_container"></div><div id="edx_notification_pane"></div>');

        this.counter_view = new CounterIconView({
            el: $("#edx_notification_container"),
            pane_el: $("#notification_pane"),

            endpoints: {
                unread_notification_count: "/count/unread",
                user_notifications: "",
                renderer_templates_urls: ""
            },
            view_templates: {
                notification_icon: "/edx_notifications/server/web/static/edx_notifications/templates/notification_icon.html",
                notification_pane: "/edx_notifications/server/web/static/edx_notifications/templates/notification_pane.html"
            }
        });
    });

    afterEach(function() {
        this.server.restore();
    });

    it("set unread notifications count url", function(){
        expect(this.counter_view.model.url).toBe("/count/unread")
    });

    it("get unread notifications count", function(){
    this.server.respondWith("GET", "/edx_notifications/server/web/static/edx_notifications/templates/notification_icon.html",
            [200, {},
             "<img class='edx-notifications-icon'/><span class='edx-notifications-count-number'><%= count %></span>"]);

    var unread_count = 2030
     this.server.respondWith("GET", "/count/unread",
            [200, { "Content-Type": "application/json" },
             '{"count":'+ unread_count +'}']);

        this.counter_view.render();
        this.server.respond();
        expect(this.counter_view.$el.html()).toContain(unread_count)
    });
});
