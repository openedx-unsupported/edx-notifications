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
                user_notifications: "/notification/pane",
                renderer_templates_urls: "/renderer/templates"
            },
            view_templates: {
                notification_icon: NotificationIcon,
                notification_pane: NotificationPane
            },
            refresh_watcher: {
                name: "none"
            }
        });
        this.counter_view.render();
    });

    afterEach(function() {
        this.server.restore();
    });

    it("set unread notifications count url", function(){
        expect(this.counter_view.model.url).toBe("/count/unread")
    });

    it("should return unread_notification_count url in endpoint", function(){
        expect(this.counter_view.endpoints.unread_notification_count).toEqual('/count/unread');
    });

    it("should return user_notifications url in endpoint", function(){
        expect(this.counter_view.endpoints.user_notifications).toBe('/notification/pane');
    });

    it("should return renderer_templates_urls in endpoints", function(){
        expect(this.counter_view.endpoints.renderer_templates_urls).toEqual('/renderer/templates');
    });

    it('get html for notification icon', function(){
        expect(this.counter_view.view_templates.notification_icon.split(" ")).toContain("count");
    });

    it('get html for notification pane', function(){
        expect(this.counter_view.view_templates.notification_pane).toContain("Notifications");
    });

    it("get unread notifications count", function(){
        var unread_count = 2030;
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

    it("should call showPane function on clicking notification icon", function(){
        var target = $(".edx-notifications-icon");
        var showPaneSpy = spyOn(this.counter_view, 'showPane');
        this.counter_view.delegateEvents();
        target.click();
        expect(showPaneSpy).toHaveBeenCalled();
    });
  });
});
})(define || RequireJS.define);
