;(function (define) {

define([
    'jquery',
    'backbone',
    'counter_icon_view',
    'text!notification_icon_template',
    'text!notification_pane_template'
], function ($, Backbone, CounterIconView, NotificationIcon, NotificationPane) {
    'use strict';

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
                notification_icon: NotificationIcon,
                notification_pane: NotificationPane
            },
            refresh_watcher: {
                name: "none"
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
        var unread_count = 2030
        this.server.respondWith(
            "GET",
            "/count/unread",
            [
                200,
                { "Content-Type": "application/json" },
                '{"count":' + unread_count + '}'
            ]
        );
        this.server.respond();
        expect(this.counter_view.$el.html()).toContain(unread_count)
    });
  });
});
})(define || RequireJS.define);
